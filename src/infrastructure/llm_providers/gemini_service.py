"""
Integracion con Google Gemini.

Este modulo encapsula la construccion de prompts y la llamada al modelo de
lenguaje utilizado por el asistente del e-commerce.
"""

import os
from typing import List

import google.generativeai as genai

from ...domain.entities import ChatContext, Product


class GeminiService:
    """
    Servicio de infraestructura para generar respuestas con Gemini.

    Attributes:
        model (genai.GenerativeModel): Modelo configurado para generar texto.
    """

    def __init__(self):
        """
        Configura el cliente de Gemini usando la variable `GEMINI_API_KEY`.

        Raises:
            ValueError: Si la clave de API no esta definida.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("models/gemini-flash-latest")

    def format_products_info(self, products: List[Product]) -> str:
        """
        Convierte productos en un bloque de texto para el prompt.

        Args:
            products (List[Product]): Productos disponibles en catalogo.

        Returns:
            str: Resumen textual listo para insertar en el prompt.
        """
        if not products:
            return "No hay productos disponibles en este momento."

        lines = []
        for product in products:
            lines.append(
                f"- {product.name} | {product.brand} | ${product.price} | Stock: {product.stock}"
            )

        return "\n".join(lines)

    async def generate_response(
        self,
        user_message: str,
        products: List[Product],
        context: ChatContext,
    ) -> str:
        """
        Genera una respuesta conversacional usando Gemini.

        Args:
            user_message (str): Mensaje actual del usuario.
            products (List[Product]): Catalogo disponible para recomendar.
            context (ChatContext): Historial reciente de la conversacion.

        Returns:
            str: Texto generado por el modelo.

        Raises:
            RuntimeError: Si ocurre un error al invocar el servicio externo.
        """
        try:
            products_info = self.format_products_info(products)
            context_text = (
                context.format_for_prompt()
                if context.messages
                else "Esta es la primera interaccion."
            )

            system_prompt = f"""
Eres un asistente virtual experto en ventas de zapatos para un e-commerce.
Tu objetivo es ayudar a los clientes a encontrar los zapatos perfectos para sus necesidades.

PRODUCTOS DISPONIBLES:
{products_info}

INSTRUCCIONES:
- Se amigable y profesional en espanol
- Usa el contexto de la conversacion anterior para mantener la coherencia
- Recomienda productos especificos cuando sea apropiado
- Menciona precios, tallas disponibles y stock cuando preguntes por productos
- Si el cliente pregunta por productos especificos, busca en la lista y proporciona detalles
- Si no tienes informacion sobre algo, se honesto y ofrece ayuda alternativa
- Manten las respuestas concisas pero informativas
- Si el cliente quiere comprar, guia hacia el proceso de compra

HISTORIAL DE CONVERSACION:
{context_text}

Usuario: {user_message}

Asistente:
"""

            response = self.model.generate_content(system_prompt)
            return response.text.strip()
        except Exception as e:
            raise RuntimeError(f"Error generando respuesta con Gemini: {str(e)}") from e
