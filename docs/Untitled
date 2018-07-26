
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 8 (class 2615 OID 24576)
-- Name: validation; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA validation;


ALTER SCHEMA validation OWNER TO postgres;

SET search_path = validation, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 190 (class 1259 OID 24594)
-- Name: annotation_question; Type: TABLE; Schema: validation; Owner: postgres
--

CREATE TABLE annotation_question (
    annotation_question_id bigint NOT NULL,
    question_name character varying(250) NOT NULL,
    question_type character varying(25) NOT NULL,
    help_text text,
    constraints text,
    date_created date NOT NULL,
    date_updated date
);


ALTER TABLE annotation_question OWNER TO postgres;

--
-- TOC entry 194 (class 1259 OID 24611)
-- Name: annotation_question_answer; Type: TABLE; Schema: validation; Owner: postgres
--

CREATE TABLE annotation_question_answer (
    annotation_question_answer_id bigint NOT NULL,
    annotation_question_id bigint NOT NULL,
    text character varying(250) NOT NULL,
    value character varying(250) NOT NULL,
    help_text text,
    date_created date NOT NULL,
    date_updated date
);


ALTER TABLE annotation_question_answer OWNER TO postgres;

--
-- TOC entry 195 (class 1259 OID 24619)
-- Name: annotation_question_answer_seq; Type: SEQUENCE; Schema: validation; Owner: postgres
--

CREATE SEQUENCE annotation_question_answer_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE annotation_question_answer_seq OWNER TO postgres;

--
-- TOC entry 191 (class 1259 OID 24599)
-- Name: annotation_question_seq; Type: SEQUENCE; Schema: validation; Owner: postgres
--

CREATE SEQUENCE annotation_question_seq
    START WITH 2
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE annotation_question_seq OWNER TO postgres;

--
-- TOC entry 188 (class 1259 OID 24587)
-- Name: annotation_set; Type: TABLE; Schema: validation; Owner: postgres
--

CREATE TABLE annotation_set (
    annotation_set_id bigint NOT NULL,
    annotation_set_definition_id bigint NOT NULL,
    cohort_name character varying(150) NOT NULL,
    cohort_source character varying(25) NOT NULL,
    cohort_id integer NOT NULL,
    owner character varying(50),
    date_created date NOT NULL,
    date_updated date
);


ALTER TABLE annotation_set OWNER TO postgres;

--
-- TOC entry 200 (class 1259 OID 24705)
-- Name: annotation_set_allocation; Type: TABLE; Schema: validation; Owner: postgres
--

CREATE TABLE annotation_set_allocation (
    annotation_set_allocation_id bigint NOT NULL,
    annotation_set_id bigint NOT NULL,
    user_id bigint NOT NULL,
    allocated_items text NOT NULL,
    date_created date NOT NULL,
    date_updated date
);


ALTER TABLE annotation_set_allocation OWNER TO postgres;

--
-- TOC entry 201 (class 1259 OID 24713)
-- Name: annotation_set_allocation_seq; Type: SEQUENCE; Schema: validation; Owner: postgres
--

CREATE SEQUENCE annotation_set_allocation_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE annotation_set_allocation_seq OWNER TO postgres;

--
-- TOC entry 186 (class 1259 OID 24577)
-- Name: annotation_set_definition; Type: TABLE; Schema: validation; Owner: postgres
--

CREATE TABLE annotation_set_definition (
    annotation_set_definition_id bigint NOT NULL,
    name character varying(150) NOT NULL,
    config text NOT NULL,
    owner character varying(150),
    date_created date NOT NULL,
    date_updated date
);


ALTER TABLE annotation_set_definition OWNER TO postgres;

--
-- TOC entry 187 (class 1259 OID 24585)
-- Name: annotation_set_definition_seq; Type: SEQUENCE; Schema: validation; Owner: postgres
--

CREATE SEQUENCE annotation_set_definition_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE annotation_set_definition_seq OWNER TO postgres;

--
-- TOC entry 192 (class 1259 OID 24604)
-- Name: annotation_set_question; Type: TABLE; Schema: validation; Owner: postgres
--

CREATE TABLE annotation_set_question (
    annotation_set_question_id bigint NOT NULL,
    annotation_set_definition_id bigint NOT NULL,
    annotation_question_id bigint NOT NULL
);


ALTER TABLE annotation_set_question OWNER TO postgres;

--
-- TOC entry 193 (class 1259 OID 24609)
-- Name: annotation_set_question_seq; Type: SEQUENCE; Schema: validation; Owner: postgres
--

CREATE SEQUENCE annotation_set_question_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE annotation_set_question_seq OWNER TO postgres;

--
-- TOC entry 196 (class 1259 OID 24621)
-- Name: annotation_set_result; Type: TABLE; Schema: validation; Owner: postgres
--

CREATE TABLE validation.annotation_set_result
(
  annotation_set_result_id bigint NOT NULL,
  annotation_set_id bigint NOT NULL,
  annontation_question_id bigint NOT NULL,
  answer_text text COLLATE pg_catalog."default",
  annotation_question_answer_id bigint,
  comment text COLLATE pg_catalog."default",
  subject_id integer,
  document_id character varying(150) COLLATE pg_catalog."default",
  user_id bigint NOT NULL,
  date_reviewed date NOT NULL,
  CONSTRAINT annotation_set_result_pkey PRIMARY KEY (annotation_set_result_id),
  CONSTRAINT annotation_set_result_question_fk FOREIGN KEY (annontation_question_id)
      REFERENCES validation.annotation_question (annotation_question_id) MATCH SIMPLE
      ON UPDATE NO ACTION
      ON DELETE NO ACTION,
  CONSTRAINT annotation_set_result_user_fk FOREIGN KEY (user_id)
      REFERENCES validation.validation_user (user_id) MATCH SIMPLE
      ON UPDATE NO ACTION
      ON DELETE NO ACTION
);


CREATE SEQUENCE annotation_set_result_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE annotation_set_result_seq OWNER TO postgres;

--
-- TOC entry 189 (class 1259 OID 24592)
-- Name: annotation_set_seq; Type: SEQUENCE; Schema: validation; Owner: postgres
--

CREATE SEQUENCE annotation_set_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE annotation_set_seq OWNER TO postgres;

--
-- TOC entry 203 (class 1259 OID 24733)
-- Name: validation_local_cohort; Type: TABLE; Schema: validation; Owner: postgres
--

CREATE TABLE validation_local_cohort (
    validation_local_cohort_def_id bigint NOT NULL,
    subject_id integer,
    document_id character varying(150)
);


ALTER TABLE validation_local_cohort OWNER TO postgres;

--
-- TOC entry 202 (class 1259 OID 24725)
-- Name: validation_local_cohort_definition; Type: TABLE; Schema: validation; Owner: postgres
--

CREATE TABLE validation_local_cohort_definition (
    validation_local_cohort_def_id bigint NOT NULL,
    validation_local_cohort_name character varying(250) NOT NULL,
    config text,
    owner character varying(250),
    cohort_type character varying(100),
    date_created date NOT NULL,
    date_updated date
);


ALTER TABLE validation_local_cohort_definition OWNER TO postgres;

--
-- TOC entry 198 (class 1259 OID 24631)
-- Name: validation_user; Type: TABLE; Schema: validation; Owner: postgres
--

CREATE TABLE validation_user (
    user_id bigint NOT NULL,
    username character varying(100) NOT NULL,
    authentication character varying(250) NOT NULL,
    authentication_method character varying(250) NOT NULL,
    date_created date NOT NULL,
    date_last_login date
);


ALTER TABLE validation_user OWNER TO postgres;

--
-- TOC entry 199 (class 1259 OID 24639)
-- Name: validation_user_seq; Type: SEQUENCE; Schema: validation; Owner: postgres
--

CREATE SEQUENCE validation_user_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE validation_user_seq OWNER TO postgres;

--
-- TOC entry 2352 (class 2606 OID 24618)
-- Name: annotation_question_answer annotation_question_answer_pkey; Type: CONSTRAINT; Schema: validation; Owner: postgres
--

ALTER TABLE ONLY annotation_question_answer
    ADD CONSTRAINT annotation_question_answer_pkey PRIMARY KEY (annotation_question_answer_id);


--
-- TOC entry 2348 (class 2606 OID 24598)
-- Name: annotation_question annotation_questions_pkey; Type: CONSTRAINT; Schema: validation; Owner: postgres
--

ALTER TABLE ONLY annotation_question
    ADD CONSTRAINT annotation_questions_pkey PRIMARY KEY (annotation_question_id);


--
-- TOC entry 2358 (class 2606 OID 24712)
-- Name: annotation_set_allocation annotation_set_allocation_pkey; Type: CONSTRAINT; Schema: validation; Owner: postgres
--

ALTER TABLE ONLY annotation_set_allocation
    ADD CONSTRAINT annotation_set_allocation_pkey PRIMARY KEY (annotation_set_allocation_id);


--
-- TOC entry 2344 (class 2606 OID 24584)
-- Name: annotation_set_definition annotation_set_definition_pkey; Type: CONSTRAINT; Schema: validation; Owner: postgres
--

ALTER TABLE ONLY annotation_set_definition
    ADD CONSTRAINT annotation_set_definition_pkey PRIMARY KEY (annotation_set_definition_id);


--
-- TOC entry 2346 (class 2606 OID 24591)
-- Name: annotation_set annotation_set_pkey; Type: CONSTRAINT; Schema: validation; Owner: postgres
--

ALTER TABLE ONLY annotation_set
    ADD CONSTRAINT annotation_set_pkey PRIMARY KEY (annotation_set_id);


--
-- TOC entry 2350 (class 2606 OID 24608)
-- Name: annotation_set_question annotation_set_question_pkey; Type: CONSTRAINT; Schema: validation; Owner: postgres
--

ALTER TABLE ONLY annotation_set_question
    ADD CONSTRAINT annotation_set_question_pkey PRIMARY KEY (annotation_set_question_id);


--
-- TOC entry 2354 (class 2606 OID 24628)
-- Name: annotation_set_result annotation_set_result_pkey; Type: CONSTRAINT; Schema: validation; Owner: postgres
--

ALTER TABLE ONLY annotation_set_result
    ADD CONSTRAINT annotation_set_result_pkey PRIMARY KEY (annotation_set_result_id);


--
-- TOC entry 2360 (class 2606 OID 24732)
-- Name: validation_local_cohort_definition validation_local_cohort_definition_pkey; Type: CONSTRAINT; Schema: validation; Owner: postgres
--

ALTER TABLE ONLY validation_local_cohort_definition
    ADD CONSTRAINT validation_local_cohort_definition_pkey PRIMARY KEY (validation_local_cohort_def_id);


--
-- TOC entry 2356 (class 2606 OID 24638)
-- Name: validation_user validation_user_pkey; Type: CONSTRAINT; Schema: validation; Owner: postgres
--

ALTER TABLE ONLY validation_user
    ADD CONSTRAINT validation_user_pkey PRIMARY KEY (user_id);


--
-- TOC entry 2364 (class 2606 OID 24655)
-- Name: annotation_question_answer annotation_question_answer_fk; Type: FK CONSTRAINT; Schema: validation; Owner: postgres
--

ALTER TABLE ONLY annotation_question_answer
    ADD CONSTRAINT annotation_question_answer_fk FOREIGN KEY (annotation_question_id) REFERENCES annotation_question(annotation_question_id);


--
-- TOC entry 2368 (class 2606 OID 24715)
-- Name: annotation_set_allocation annotation_set_allocation_as_fk; Type: FK CONSTRAINT; Schema: validation; Owner: postgres
--

ALTER TABLE ONLY annotation_set_allocation
    ADD CONSTRAINT annotation_set_allocation_as_fk FOREIGN KEY (annotation_set_id) REFERENCES annotation_set(annotation_set_id);


--
-- TOC entry 2369 (class 2606 OID 24720)
-- Name: annotation_set_allocation annotation_set_allocation_user_fk; Type: FK CONSTRAINT; Schema: validation; Owner: postgres
--

ALTER TABLE ONLY annotation_set_allocation
    ADD CONSTRAINT annotation_set_allocation_user_fk FOREIGN KEY (user_id) REFERENCES validation_user(user_id);


--
-- TOC entry 2361 (class 2606 OID 24650)
-- Name: annotation_set annotation_set_def_annotation_set_fk; Type: FK CONSTRAINT; Schema: validation; Owner: postgres
--

ALTER TABLE ONLY annotation_set
    ADD CONSTRAINT annotation_set_def_annotation_set_fk FOREIGN KEY (annotation_set_definition_id) REFERENCES annotation_set_definition(annotation_set_definition_id);


--
-- TOC entry 2363 (class 2606 OID 24700)
-- Name: annotation_set_question annotation_set_question_definition_fk; Type: FK CONSTRAINT; Schema: validation; Owner: postgres
--

ALTER TABLE ONLY annotation_set_question
    ADD CONSTRAINT annotation_set_question_definition_fk FOREIGN KEY (annotation_set_definition_id) REFERENCES annotation_set_definition(annotation_set_definition_id);


--
-- TOC entry 2362 (class 2606 OID 24665)
-- Name: annotation_set_question annotation_set_question_question_fk; Type: FK CONSTRAINT; Schema: validation; Owner: postgres
--

ALTER TABLE ONLY annotation_set_question
    ADD CONSTRAINT annotation_set_question_question_fk FOREIGN KEY (annotation_question_id) REFERENCES annotation_question(annotation_question_id);


--
-- TOC entry 2366 (class 2606 OID 24675)
-- Name: annotation_set_result annotation_set_result_ans_fk; Type: FK CONSTRAINT; Schema: validation; Owner: postgres
--

ALTER TABLE ONLY annotation_set_result
    ADD CONSTRAINT annotation_set_result_ans_fk FOREIGN KEY (annotation_question_answer_id) REFERENCES annotation_question_answer(annotation_question_answer_id);


--
-- TOC entry 2365 (class 2606 OID 24670)
-- Name: annotation_set_result annotation_set_result_as_fk; Type: FK CONSTRAINT; Schema: validation; Owner: postgres
--

ALTER TABLE ONLY annotation_set_result
    ADD CONSTRAINT annotation_set_result_as_fk FOREIGN KEY (annotation_set_id) REFERENCES annotation_set(annotation_set_id);


--
-- TOC entry 2367 (class 2606 OID 24680)
-- Name: annotation_set_result annotation_set_result_user_fk; Type: FK CONSTRAINT; Schema: validation; Owner: postgres
--

ALTER TABLE ONLY annotation_set_result
    ADD CONSTRAINT annotation_set_result_user_fk FOREIGN KEY (user_id) REFERENCES validation_user(user_id);


-- Completed on 2017-02-01 10:49:18 EST

--
-- PostgreSQL database dump complete
--
