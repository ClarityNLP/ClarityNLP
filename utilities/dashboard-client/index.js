const express = require("express");
const bodyParser = require("body-parser");
var cors = require("cors");
const axios = require("axios");
const dotenv = require("dotenv");

dotenv.config();

const app = express();

app.use(bodyParser.json());
app.use(cors());

app.get("/", (req, res) => {
    res.send("Welcome to the ClarityNLP dashboard API!");
});

app.get("/document_sources", (req, res) => {
    const url =
        process.env.SOLR_API_URL +
        "sample/select?facet.field=source&facet=on&fl=facet_counts&indent=on&q=*:*&rows=1&wt=json";

    axios
        .get(url)
        .then(response => {
            res.send(response.data);
        })
        .catch(err => {
            res.send(err);
        });
});

app.get("/jobs", (req, res) => {
    const url = process.env.CLARITY_NLP_URL + "phenotype_jobs/ALL";

    axios
        .get(url)
        .then(response => {
            res.send(response.data);
        })
        .catch(err => {
            res.send(err);
        });
});

app.get("/library", (req, res) => {
    const url = process.env.CLARITY_NLP_URL + "library";

    axios
        .get(url)
        .then(response => {
            res.send(response.data);
        })
        .catch(err => {
            res.send(err);
        });
});

const port = 8750;

app.listen(port, () => {
    console.log(`Server started on http://localhost:${port}`);
});
