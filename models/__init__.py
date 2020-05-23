import config
import mongoengine

if config.MONGO_URI:
	mongoengine.connect(config.DB_NAME, host=config.MONGO_URI, alias="default")
else:
	mongoengine.connect(config.DB_NAME, host=config.MONGO_HOST, port=config.MONGO_PORT, alias="default")