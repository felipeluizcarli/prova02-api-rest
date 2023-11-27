import random

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlmodel import select

from src.config.database import get_session
from src.models.reservas_model import Reserva
from src.models.voos_model import Voo

reservas_router = APIRouter(prefix="/reservas")


@reservas_router.get("/{id_voo}")
def lista_reservas_voo(id_voo: int):
    with get_session() as session:
        statement = select(Reserva).where(Reserva.voo_id == id_voo)
        reservas = session.exec(statement).all()
        return reservas


@reservas_router.post("")
def cria_reserva(reserva: Reserva):
    with get_session() as session:
        voo = session.exec(select(Voo).where(Voo.id == reserva.voo_id)).first()

        if not voo:
            return JSONResponse(
                content={"message": f"Voo com id {reserva.voo_id} não encontrado."},
                status_code=404,
            )

        # TODO - Validar se existe uma reserva para o mesmo documento

        codigo_reserva = "".join(
            [str(random.randint(0, 999)).zfill(3) for _ in range(2)]
        )

        reserva.codigo_reserva = codigo_reserva
        session.add(reserva)
        session.commit()
        session.refresh(reserva)
        return reserva


@reservas_router.post("/{codigo_reserva}/checkin/{num_poltrona}")
def faz_checkin(codigo_reserva: str, num_poltrona: int):
    
    @reservas_router.post("")
def cria_reserva(reserva: Reserva):
    with get_session() as session:
        # Verificar se já existe uma reserva para o mesmo documento
        existing_reserva = session.exec(
            select(Reserva).where(Reserva.documento == reserva.documento)
        ).first()

        if existing_reserva:
            return JSONResponse(
                content={"message": "Já existe uma reserva para este documento."},
                status_code=400,
            )

        voo = session.exec(select(Voo).where(Voo.id == reserva.voo_id)).first()

        if not voo:
            return JSONResponse(
                content={"message": f"Voo com id {reserva.voo_id} não encontrado."},
                status_code=404,
            )

        codigo_reserva = "".join(
            [str(random.randint(0, 999)).zfill(3) for _ in range(2)]
        )

        reserva.codigo_reserva = codigo_reserva
        session.add(reserva)
        session.commit()
        session.refresh(reserva)
        return reserva

# TODO - Implementar troca de reserva de poltrona

@reservas_router.post("/{codigo_reserva}/checkin/{num_poltrona}")
def faz_checkin(codigo_reserva: str, num_poltrona: int):
    with get_session() as session:
        reserva = session.exec(
            select(Reserva).where(Reserva.codigo_reserva == codigo_reserva)
        ).first()

        if not reserva:
            return JSONResponse(
                content={"message": f"Reserva com código {codigo_reserva} não encontrada."},
                status_code=404,
            )

        voo = session.exec(select(Voo).where(Voo.id == reserva.voo_id)).first()

        if not voo:
            return JSONResponse(
                content={"message": f"Voo com id {reserva.voo_id} não encontrado."},
                status_code=404,
            )

        # poltrona esta livre
        poltrona_field = f"poltrona_{num_poltrona}"
        if getattr(voo, poltrona_field):
            return JSONResponse(
                content={"message": f"Poltrona {num_poltrona} já ocupada."},
                status_code=403,
            )

        /// Atualizar poltrona com o código da reserva
        
        setattr(voo, poltrona_field, reserva.codigo_reserva)
        session.commit()

        return {"message": f"Check-in realizado com sucesso na poltrona {num_poltrona}."}

        @reservas_router.patch("/{codigo_reserva}/checkin/{num_poltrona}")
def troca_checkin(codigo_reserva: str, num_poltrona: int):
    with get_session() as session:
        reserva = session.exec(
            select(Reserva).where(Reserva.codigo_reserva == codigo_reserva)
        ).first()

        if not reserva:
            return JSONResponse(
                content={"message": f"Reserva com código {codigo_reserva} não encontrada."},
                status_code=404,
            )

        voo = session.exec(select(Voo).where(Voo.id == reserva.voo_id)).first()

        if not voo:
            return JSONResponse(
                content={"message": f"Voo com id {reserva.voo_id} não encontrado."},
                status_code=404,
            )

        # poltrona ocupada
        poltrona_field = f"poltrona_{num_poltrona}"
        if getattr(voo, poltrona_field) != reserva.codigo_reserva:
            return JSONResponse(
                content={"message": f"Poltrona {num_poltrona} não está ocupada por esta reserva."},
                status_code=403,
            )

        # Trocar poltrona
        nova_poltrona_field = f"poltrona_{num_poltrona + 1}"  
        if not getattr(voo, nova_poltrona_field):
            setattr(voo, nova_poltrona_field, reserva.codigo_reserva)
            setattr(voo, poltrona_field, None)
            session.commit()

            return {"message": f"Troca de poltrona realizada com sucesso."}

        return JSONResponse(
            content={"message": f"Não foi possível trocar para a poltrona {num_poltrona + 1}."},
            status_code=403,
        )
