import os
import cv2
import numpy as np
import base64
import easyocr
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from graph_state import WorkbenchState

# 1. Initialize globally on CPU to save VRAM (gpu=False)
reader = easyocr.Reader(['en'], gpu=False)

def preprocess_image_for_ocr(image_path: str) -> np.ndarray:
    """
    Reads and preprocesses an image for optimal OCR extraction, especially 
    designed for noisy industrial scans.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")
        
    # Read image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Failed to read image at path: {image_path}")
        
    # Apply slight Gaussian blur (3x3) to remove scanner noise
    blurred = cv2.GaussianBlur(img, (3, 3), 0)
    
    # Apply adaptive threshold to make faded text/handwriting pop out against background
    processed_img = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    return processed_img

def extract_and_map_spatial_grid(image_path: str) -> str:
    """
    Core Algorithm: Extracts text and maps it spatially to preserve rows and columns.
    """
    processed_img = preprocess_image_for_ocr(image_path)
    
    # Pass processed image to easyocr
    results = reader.readtext(processed_img)
    
    valid_blocks = []
    # 1. Extract bounding boxes, text, and confidence. Ignore confidence < 0.25.
    for bbox, text, conf in results:
        if conf < 0.25:
            continue
            
        # bbox format: [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
        # 2. Calculate the center (x, y) of each bounding box.
        x_coords = [p[0] for p in bbox]
        y_coords = [p[1] for p in bbox]
        center_x = sum(x_coords) / 4.0
        center_y = sum(y_coords) / 4.0
        
        valid_blocks.append({
            'text': text,
            'x': center_x,
            'y': center_y
        })
        
    if not valid_blocks:
        return ""
        
    # Initial sort by y to help with row clustering
    valid_blocks.sort(key=lambda b: b['y'])
    
    # 3. Group text blocks into rows by clustering the y coordinates
    rows = []
    current_row = [valid_blocks[0]]
    
    for block in valid_blocks[1:]:
        row_avg_y = sum(b['y'] for b in current_row) / len(current_row)
        # If the Y-center is within 15 pixels of the current row's average, add to it
        if abs(block['y'] - row_avg_y) <= 15:
            current_row.append(block)
        else:
            rows.append(current_row)
            current_row = [block]
    if current_row:
        rows.append(current_row)
        
    mapped_text_lines = []
    for row in rows:
        # 4. Within each row, sort the text blocks by their x coordinate.
        row.sort(key=lambda b: b['x'])
        # 5. Format the output string so columns are visually separated by " | "
        row_text = " | ".join(b['text'] for b in row)
        mapped_text_lines.append(row_text)
        
    return "\n".join(mapped_text_lines)

def encode_image_to_base64(image_path: str) -> str:
    """Encodes an image to a base64 string for the Vision LLM."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def vision_node(state: WorkbenchState) -> dict:
    """
    Vision Node: Processes complex images using spatial mapping and a Vision LLM.
    """
    active_plan = state.get("active_plan", [])
    image_path = state.get("image_path")
    
    # Check if vision task is required
    if "vision" not in active_plan or not image_path:
        return {"extracted_vision_data": "No vision task required."}
        
    try:
        # Get spatially mapped text
        spatial_text = extract_and_map_spatial_grid(image_path)
        base64_image = encode_image_to_base64(image_path)
        
        # Initialize vision LLM. keep_alive=0 is critical for 6GB VRAM constraint.
        vision_llm = ChatOllama(model="llava-phi3", temperature=0.0, keep_alive=0)
        
        # Construct the prompt
        prompt_text = f"""You are an elite data extraction agent for industrial reports. I have algorithmically extracted the text and its spatial layout from this image. 

RAW SPATIAL DATA:
{spatial_text}

Look at the image and the RAW SPATIAL DATA. Format this data into a clean, professional Markdown document (use tables if it's a tabular report, or headers/lists). Rule: DO NOT hallucinate or calculate any numbers. Use ONLY the data provided in the RAW SPATIAL DATA."""

        # Construct HumanMessage with text and image
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt_text},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                }
            ]
        )
        
        # Invoke the model
        response = vision_llm.invoke([message])
        return {"extracted_vision_data": response.content}
        
    except Exception as e:
        return {"extracted_vision_data": f"Error during vision processing: {str(e)}"}

if __name__ == "__main__":
    # Test Harness
    mock_state: WorkbenchState = {
        "user_query": "Extract the table from the industrial scan.",
        "image_path": "sample.png",
        "active_plan": ["vision"],
        "extracted_vision_data": "",
        "retrieved_documents": "",
        "sandbox_code": "",
        "execution_logs": "",
        "evaluator_feedback": "",
        "retry_count": 0,
        "final_deliverable_path": ""
    }
    
    print("Testing Vision Node (Beast Mode)...")
    
    # Create a dummy image for testing if it doesn't exist
    if not os.path.exists("sample.png"):
        print("Creating a dummy sample.png for testing...")
        dummy_img = np.zeros((200, 400), dtype=np.uint8)
        # Adding some dummy tabular data
        cv2.putText(dummy_img, "ID | Name | Score", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,), 2)
        cv2.putText(dummy_img, "01 | Test | 99", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,), 2)
        cv2.imwrite("sample.png", dummy_img)
        
    try:
        result = vision_node(mock_state)
        print("\n=== Extracted Vision Data ===")
        print(result.get("extracted_vision_data"))
    except Exception as e:
        print(f"Execution failed: {e}")
