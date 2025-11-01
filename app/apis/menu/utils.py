import base64
import requests
from apis.menu import schemas
from db.models import MenuItem
from fastapi import HTTPException
from urllib.parse import urlparse

extensionesImaPermitida:(".jpg",".png",".webp," ".jpeg" )
dominiosPermitidos:("storage.googleapis.com","usercontent.google.com")

def safe_url (image_url: str):
    url = urlparse(image_url)

    if url.scheme not in ("http", "https"):
        raise ValueError("Url no permitida, debe de ser http o https")
    if url.hostname not in dominiosPermitidos:
        raise ValueError("imagenes sacadas de dominios no permitidos")
    if url.path.lower().endswith(extensionesImaPermitida):
        raise ValueError("formato de imagen no permitda")

    return image_url

def _image_url_to_base64(image_url: str):
    safe_url(image_url)
    response = requests.get(image_url, stream=True)
    encoded_image = base64.b64encode(response.content).decode()

    return encoded_image


def create_menu_item(
    db,
    menu_item: schemas.MenuItemCreate,
):
    menu_item_dict = menu_item.dict()
    image_url = menu_item_dict.pop("image_url", None)
    db_item = MenuItem(**menu_item_dict)

    if image_url:
        db_item.image_base64 = _image_url_to_base64(image_url)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item


def update_menu_item(
    db,
    item_id: int,
    menu_item: schemas.MenuItemCreate,
):
    db_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")

    menu_item_dict = menu_item.dict()
    image_url = menu_item_dict.pop("image_url", None)

    for key, value in menu_item_dict.items():
        setattr(db_item, key, value)

    if image_url:
        db_item.image_base64 = _image_url_to_base64(image_url)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_menu_item(db, item_id: int):
    db_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")

    db.delete(db_item)
    db.commit()
