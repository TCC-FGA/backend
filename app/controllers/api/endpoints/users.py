from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.api import deps
from app.controllers.api import api_messages
from app.core.config import get_settings
from app.core.security.jwt import generate_reset_token, verify_reset_token
from app.core.security.password import get_password_hash
from app.models.models import Owner as User
from app.schemas.map_responses import map_user_to_response
from app.schemas.requests import UserUpdatePasswordRequest, UserUpdateRequest, PasswordResetRequest, PasswordResetConfirmRequest
from app.schemas.responses import UserResponse
import requests

router = APIRouter()


@router.get("/me", response_model=UserResponse, description="Get current user")
async def read_current_user(
    current_user: User = Depends(deps.get_current_user),
) -> UserResponse:
    return map_user_to_response(current_user)

@router.patch("/me", response_model=UserResponse, description="Update current user")
async def update_current_user(
    user_data: UserUpdateRequest,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> UserResponse:
    
    result = await session.execute(select(User).where(User.user_id == current_user.user_id))
    user = result.scalars().first()
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.telefone = user_data.telephone if user_data.telephone is not None else user.telefone
    user.nome = user_data.name if user_data.name is not None else user.nome
    user.assinatura_hash = user_data.hashed_signature if user_data.hashed_signature is not None else user.assinatura_hash
    
    await session.commit()
    await session.refresh(user)

    return map_user_to_response(current_user)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete current user",
)
async def delete_current_user(
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
) -> None:
    await session.execute(delete(User).where(User.user_id == current_user.user_id))
    await session.commit()


@router.post(
    "/reset-password",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Update current user password",
)
async def reset_current_user_password(
    user_update_password: UserUpdatePasswordRequest,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> None:
    current_user.senha_hash = get_password_hash(user_update_password.password)
    session.add(current_user)
    await session.commit()


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request: PasswordResetRequest,
    session: AsyncSession = Depends(deps.get_session)
):
    try:
        result = await session.execute(select(User).where(User.email == request.email))
        user = result.scalars().first()

        if not user:
            return {"detail": "Se um usuário com este email existir, um link para redefinição de senha será enviado."}
        
        reset_token = generate_reset_token(user.email)
        url_service_mail = get_settings().security.email_host.get_secret_value()
        
        response = requests.post(
            url_service_mail,
            json={"email": user.email, "token": reset_token }
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Falha ao enviar o email de redefinição de senha"
            )

        return {"detail": "Se um usuário com este email existir, um link para redefinição de senha será enviado."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Falha ao enviar o email de redefinição de senha"
        )


@router.post("/reset-password/confirm", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    request: PasswordResetConfirmRequest,
    session: AsyncSession = Depends(deps.get_session)
):
    try:
        if request.new_password != request.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="As senhas não coincidem"
            )
        email = verify_reset_token(request.token)
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido ou expirado"
            )

        result = await session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

        user.senha_hash = get_password_hash(request.new_password)
        session.add(user)
        await session.commit()

        return {"detail": "Senha redefinida com sucesso."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Falha ao redefinir a senha"
        )