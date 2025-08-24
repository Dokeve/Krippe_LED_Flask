from dotenv import load_dotenv
load_dotenv()
class Config:
    SECRET_KEY='dev'
    LED_COUNT=997
    LED_BRIGHTNESS=180
    LED_DRIVER='dummy'
    LED_PIN=18
    AUDIO_VOLUME=0.5
    DUCKED_VOLUME=0.2
    GPIO_VOICE_FILE='assets/voice_clip.wav'
    DB_HOST='127.0.0.1'
    DB_PORT=3306
    DB_NAME='led_db'
    DB_USER='led_user'
    DB_PASS='led_pass'
    @classmethod
    def db_uri(cls):
        return f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASS}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
