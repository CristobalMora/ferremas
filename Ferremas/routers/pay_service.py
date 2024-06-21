from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import requests
from Ferremas.sql_app import crud
from Ferremas.sql_app.dependencies import get_db

router = APIRouter()

@router.post("/pay-service/", response_model=dict, tags=["Payment Service"])
def pay_service(user_email: str, service_name: str, db: Session = Depends(get_db)):
    # Verificar si el usuario existe en la base de datos
    db_user = crud.get_user_by_email(db, email=user_email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Información del servicio a pagar
    service_amount = 5000  # Ejemplo de monto en pesos

    # Llamar a la API para pagar el servicio
    url = "https://webpay3gint.transbank.cl/rswebpaytransaction/api/webpay/v1.2/transactions"
    headers = {
        "Tbk-Api-Key-Id": "597055555532",
        "Tbk-Api-Key-Secret": "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C",
        "Content-Type": "application/json"
    }
    payload = {
        "buy_order": f"{user_email}-{service_name}",
        "session_id": f"{user_email}-{service_name}",
        "amount": service_amount,
        "return_url": "http://www.comercio.cl/webpay/retorno"
    }
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        # La solicitud fue exitosa
        return {"message": "Payment request successful", "transaction_details": response.json()}
    else:
        # La solicitud falló
        return {"error": f"Error sending payment request: {response.status_code} - {response.text}"}
