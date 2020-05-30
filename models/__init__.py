import config
import mongoengine

if config.MONGO_HOST and config.MONGO_PORT:
	mongoengine.connect(
		config.DB_NAME, 
		host=config.MONGO_HOST, 
		port=int(config.MONGO_PORT),
		username=config.MONGO_USERNAME,
		password=config.MONGO_PASSWORD,
		alias="default"
	)
else:
	mongoengine.connect(config.DB_NAME, host=config.MONGO_URI, alias="default")