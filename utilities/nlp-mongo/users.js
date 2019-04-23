db.createUser(
  {
    user: process.env.INGEST_MONGO_USERNAME,
    pwd: process.env.INGEST_MONGO_PASSWORD,
    roles:[
      {
        role: "dbOwner",
        db:   "nlp"
      }
    ]
  }
);
