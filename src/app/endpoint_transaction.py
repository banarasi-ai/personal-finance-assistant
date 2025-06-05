import json
from http import HTTPStatus
from typing import List
import pandas as pd
import io
from fastapi import APIRouter, UploadFile
from starlette.responses import Response, StreamingResponse
from data_model.transaction_model import Transaction, TransactionBase
from datetime import datetime as dt


router = APIRouter()

transactions = []

prices = []


# @router.post("/", dependencies=[])
# def handle_event(
#     data: EventSchema,
# ) -> Response:
#     print(data)

#     # This is where you implement the AI logic to handle the event

#     # Return acceptance response
#     return Response(
#         content=json.dumps({"message": "Data received!"}),
#         status_code=HTTPStatus.ACCEPTED,
#     )

@router.post("/", dependencies=[])
def handle_transaction(
    data: TransactionBase,
) -> Response:
    """Handles incoming transaction and stores it in memory."""
    print(f"data is {data}")
    transaction_id = len(transactions)
    #transaction_dict = TransactionBase.model_json_schema()["properties"]
    #transaction_dict = BaseModel.model_dump(TransactionBase)
    transaction_dict= data.model_dump()
    transaction_dict["transaction_id"] = transaction_id
    transaction_record = Transaction(**transaction_dict)
    transactions.append(transaction_record)
    # This is where you implement the AI logic to handle the event

    # Return acceptance response
    return Response(
        content=json.dumps({"message": "Data received!"}),
        status_code=HTTPStatus.ACCEPTED,
    )
    
@router.get("/", response_model=List[Transaction])
def get_transactions(
):
    """Retrieves all transactions."""
    return transactions

@router.get("/download/", response_class=StreamingResponse)
async def export_data():
    # Create a sample dataframe
    df = pd.DataFrame([t.model_dump() for t in transactions]).drop(columns=["transaction_id"])
    df["transaction_date_str"] = df["transaction_date"].dt.strftime('%Y-%m-%d %H:%M:%S')
    df = df.drop(columns=["transaction_date"])
    df.rename(columns={"transaction_date_str": "transaction_date"}, inplace=True)
    df.set_index("transaction_date", inplace=True)
    df.reset_index(inplace=True)    
    
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    response = StreamingResponse(
        iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=transactions_export.csv"
    return response

@router.post("/upload/")
async def upload_file(file: UploadFile):
    # do something with the file
    if file.content_type != 'text/csv':
        return Response(
            content=json.dumps({"message": "Only CSV files are allowed!"}),
            status_code=HTTPStatus.BAD_REQUEST,
        )
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode('utf-8')), header=0, index_col=None, skiprows=0)
    df["transaction_additional_info"] = df["transaction_additional_info"].fillna("").astype(str)
    for _, row in df.iterrows():
        transaction_dict = TransactionBase(**row.to_dict()).model_dump()
        transaction_id = len(transactions)
        transaction_dict["transaction_id"] = transaction_id
        transaction_record = Transaction(**transaction_dict)
        transactions.append(transaction_record)
    return {"filename": file.filename}