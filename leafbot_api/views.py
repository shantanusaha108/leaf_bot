from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import ChatLog
from .serializers import ChatLogSerializer
from leafbot_project.services.google_ai_service import query_gemini
from logger import log_error

class DiagnoseView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        user_text = request.data.get('text', '').strip()
        language = request.data.get('language', 'en')
        image = request.data.get('image')

        if not image and not user_text:
            log_error("InputError", "No image or text provided by user")
            return Response(
                {'error': 'Please provide an image, text, or both'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            final_prompt = user_text or "No description provided"
            final_prompt += f" Respond in {language}."

            gemini_response = query_gemini(
                description=final_prompt,
                language=language,
                image=image if image else None
            )
            if "Error:" in gemini_response:
                log_error("CohereAPI", gemini_response)
                return Response({'error': 'Cohere API call failed'}, 
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            chat_log = ChatLog.objects.create(
                user_text=user_text or "No description provided",
                image=image if image else None,
                response_text=gemini_response
            )

            return Response(ChatLogSerializer(chat_log).data)

        except Exception as e:
            log_error("ServerError", str(e))
            return Response(
                {"error": "Internal server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
