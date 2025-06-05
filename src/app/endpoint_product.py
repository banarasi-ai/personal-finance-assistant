import json
from http import HTTPStatus
from typing import List
import pandas as pd
import io
from fastapi import APIRouter, UploadFile
from starlette.responses import Response, StreamingResponse
from data_model.product_model import ProductPrice, ProductPriceBase
from datetime import datetime as dt

router = APIRouter()

products = []


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
def handle_product_price(
    data: ProductPriceBase,
) -> Response:
    """Handles incoming product price and stores it in memory."""
    print(f"data is {data}")
    product_id = len(products)
    #product_dict = ProductPriceBaseSchema.model_json_schema()["properties"]
    #product_dict = BaseModel.model_dump(ProductPriceBaseSchema)
    product_dict= data.model_dump()
    product_dict["product_id"] = product_id
    product_record = ProductPrice(**product_dict)
    products.append(product_record)
    # This is where you implement the AI logic to handle the event

    # Return acceptance response
    return Response(
        content=json.dumps({"message": "Data received!"}),
        status_code=HTTPStatus.ACCEPTED,
    )

@router.get("/", response_model=List[ProductPrice])
def get_product_prices(
):
    """Retrieves all product prices."""
    return products

@router.get("/download/", response_class=StreamingResponse)
async def export_data():
    # Create a sample dataframe
    df = pd.DataFrame([t.model_dump() for t in products]).drop(columns=["product_id"])
    df["product_search_date_str"] = df["product_search_date"].dt.strftime('%Y-%m-%d %H:%M:%S')
    df = df.drop(columns=["product_search_date"])
    df.rename(columns={"product_search_date_str": "product_search_date"}, inplace=True)
    df.set_index("product_search_date", inplace=True)
    df.reset_index(inplace=True)
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    response = StreamingResponse(
        iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=product_prices_export.csv"
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
    df["product_additional_info"] = df["product_additional_info"].fillna("").astype(str)
    for _, row in df.iterrows():
        product_dict = ProductPriceBase(**row.to_dict()).model_dump()
        product_id = len(products)
        product_dict["product_id"] = product_id
        product_record = ProductPrice(**product_dict)
        products.append(product_record)
    return {"filename": file.filename}