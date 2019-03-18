db.createUser(
  {
    user: "admin",
    pwd: "password",
    roles:[
      {
        role: "dbOwner",
        db:   "ingest"
      }
    ]
  }
);
