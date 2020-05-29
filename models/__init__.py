import config
import mongoengine

if config.MONGO_HOST:
	mongoengine.connect(config.DB_NAME, host=config.MONGO_HOST, port=int(config.MONGO_PORT), alias="default")
else:
	mongoengine.connect(config.DB_NAME, host=config.MONGO_URI, alias="default")