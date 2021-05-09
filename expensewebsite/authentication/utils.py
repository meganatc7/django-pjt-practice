from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type

# PasswordResetTokenGenerator는 장고에서 제공하는 class로 비밀번호 리셋할 때 token을발급해줌
class AppTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        # text_type은 유니코드 정수로부터 유니코드 문자열을 가져옴
        return (text_type(user.is_active) + text_type(user.pk) + text_type(timestamp))

token_generator = AppTokenGenerator()