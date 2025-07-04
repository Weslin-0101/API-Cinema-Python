from typing import Optional
from passlib.context import CryptContext

from sqlalchemy.orm import Session

from app.models.reserva import ItemReserva, Reserva
from app.models.schemas.enum.enum_util import StatusReservaEnum
from app.models.schemas.item_reserva_schema import ItemReservaCreate

class ItemReservaService:
    def __init__(self):
        self.pwd_context = CryptContext(deprecated="auto")

    def search_item_by_id(self, db: Session, item_id: int) -> Optional[ItemReserva]:
        return db.query(ItemReserva).filter(ItemReserva.reserva_id == item_id).all()
    
    def add_item_reserve(
        self,
        reserve_id: int,
        item_data: ItemReservaCreate,
        db: Session
    ) -> Optional[ItemReserva]:
        reserve = db.query(Reserva).filter(Reserva.id == reserve_id).first()
        if not reserve:
            raise ValueError("Reserva não encontrada")
        
        if reserve.status != StatusReservaEnum.PENDENTE.value:
            raise ValueError("Não é possível adicionar itens pendentes")
        
        item = ItemReserva(
            reserva_id=reserve_id,
            item_id=item_data.item_id,
            tipo=item_data.tipo,
            quantidade=item_data.quantidade,
            preco_unitario=item_data.preco_unitario,
            preco_total=item_data.preco_total,
            desconto=item_data.desconto
        )

        db.add(item)

        new_value = item_data.preco_total - item_data.desconto
        reserve.valor_total += new_value

        db.commit()
        db.refresh(item)

        return item
    
    def remove_item_reserve(
        self,
        item_id: int,
        db: Session
    ) -> bool:
        item = self.search_item_by_id(db, item_id)
        if not item:
            return False
        
        reserve = db.query(Reserva).filter(Reserva.id == item.reserva_id).first()
        if reserve.status != StatusReservaEnum.PENDENTE.value:
            raise ValueError("Não é possível remover itens pendentes")
        
        value_item = item.preco_total - item.desconto
        reserve.valor_total -= value_item

        db.delete(item)
        db.commit()

        return True
    
item_reserva_service = ItemReservaService()