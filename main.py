from fastapi import FastAPI, UploadFile, File
import pytesseract
import cv2
import numpy as np
import re

app = FastAPI()

def clean_and_extract_moves(raw_text):
    """
    Takes raw OCR text and extracts valid chess moves based on English algebraic notation.
    """
    chess_move_pattern = re.compile(
        r'\b([KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](?:=[QRBN])?[+#]?[!?]*|(?:O-O(?:-O)?|0-0(?:-0)?)[+#]?[!?]*)\b'
    )
    result_pattern = re.compile(r'(1-0|0-1|1/2-1/2)')
    
    moves = []
    lines = raw_text.split('\n')
    
    for line in lines:
        found_moves = chess_move_pattern.findall(line)
        if found_moves:
            moves.extend(found_moves)
            
    result = result_pattern.search(raw_text)
    game_result = result.group(0) if result else "*"
    
    return format_to_pgn(moves, game_result)

def format_to_pgn(moves, result):
    """
    Formats a list of sequential moves into a standard PGN string.
    """
    pgn_string = ""
    move_number = 1
    
    for i in range(0, len(moves), 2):
        white_move = moves[i]
        black_move = moves[i+1] if (i + 1) < len(moves) else ""
        pgn_string += f"{move_number}. {white_move} {black_move} "
        move_number += 1
        
    pgn_string += result
    return pgn_string.strip()

# --- API ENDPOINTS ---

@app.get("/")
def home():
    """A simple check to ensure the server is awake."""
    return {"message": "Chess OCR API is running!"}

@app.post("/scan/")
async def scan_chess_sheet(file: UploadFile = File(...)):
    """
    Receives an image file from the mobile app, processes it, and returns PGN.
    """
    try:
        # Read the image file securely sent from the phone
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convert to grayscale and threshold for OCR clarity
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        # Run Tesseract OCR
        raw_text = pytesseract.image_to_string(thresh)
        
        # Parse the extracted text into PGN format
        pgn_output = clean_and_extract_moves(raw_text)
        
        return {"success": True, "pgn": pgn_output}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
