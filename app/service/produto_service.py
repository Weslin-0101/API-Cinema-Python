from typing import List, Optional
from fastapi import HTTPException, status
from passlib.context import CryptContext

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import Produto
from app.models.schemas.produto_schema import ProdutoCreate, ProdutoUpdate

class ProdutoService:
    def __init__(self):
        self.pwd_context = CryptContext(deprecated="auto")

    def create_product(self, db: Session, product_data: ProdutoCreate) -> Produto:
        try:
            product_dict = product_data.model_dump()

            db_product = Produto(**product_dict)
            db.add(db_product)
            db.commit()
            db.refresh(db_product)

            return db_product
        
        except IntegrityError as e:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao criar produto."
            )
        
    def get_product_by_id(self, db: Session, product_id: int) -> Optional[Produto]:
        return db.query(Produto).filter(Produto.id == product_id).first()
    
    def get_product_by_name(self, db: Session, product_name: str) -> Optional[Produto]:
        return db.query(Produto).filter(Produto.nome == product_name).first()
    
    def get_products(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        ativo: Optional[bool] = None
    ) -> List[Produto]:
        query = db.query(Produto)

        if ativo is not None:
            query = query.filter(Produto.ativo == ativo)

        return query.offset(skip).limit(limit).all()
    
    def update_product(
        self,
        db: Session,
        product_id: int,
        product_data: ProdutoUpdate
    ) -> Optional[Produto]:
        db_product = self.get_product_by_id(db, product_id)

        if not db_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado."
            )
        
        try:
            for key, value in product_data.model_dump(exclude_unset=True).items():
                setattr(db_product, key, value)

            db.add(db_product)
            db.commit()
            db.refresh(db_product)

            return db_product
        
        except IntegrityError as e:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar produto."
            )

    def partial_delete_product(
        self,
        db: Session,
        product_id: int
    ) -> bool:
        db_product = self.get_product_by_id(db, product_id)

        if not db_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado."
            )
        
        db_product.disponivel = False
        db.add(db_product)
        db.commit()
        db.refresh(db_product)

        return True
    
    def permanent_delete_product(
        self,
        db: Session,
        product_id: int
    ) -> bool:
        db_product = self.get_product_by_id(db, product_id)

        if not db_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado."
            )
        
        db.delete(db_product)
        db.commit()
        
        return True
        
produto_service = ProdutoService()