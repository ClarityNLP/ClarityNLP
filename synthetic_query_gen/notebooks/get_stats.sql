SELECT
  nlp_job_id,
  name,
  job_type,
  job_index,
  status,
  date_started,
  date_ended,
  extract(HOUR FROM total_time) * 60 +
  extract(MINUTE FROM total_time) AS
                                     total_minutes,
  extract(SECOND FROM total_time)    total_seconds,
  CASE WHEN feature_count IS NULL
    THEN '0'
  ELSE feature_count END          AS feature_count,
  CASE WHEN patient_count IS NULL
    THEN '0'
  ELSE patient_count END          AS patient_count,
  luigi_workers,
  batch_size,
  memory_caching,
  precomputed_segmentation,
  reordered_nlpql,
  chained_queries,
  redis_cache,
  cache_hit_ratio,
  cache_compute_count,
  cache_query_count
FROM
  (SELECT
     nj.nlp_job_id,
     nj.name,
     nj.spl [1]                                   AS job_type,
     nj.spl [3]                                   AS job_index,
     nj.status,
     nj.date_started,
     nj.date_ended,
     ((CASE WHEN nj.date_ended IS NULL
       THEN current_timestamp
       ELSE nj.date_ended END) - nj.date_started) AS total_time,

     CASE WHEN c.description = '0'
       THEN f.description
     ELSE c.description END                       AS feature_count,
     CASE WHEN d.description = '0'
       THEN g.description
     ELSE d.description END                       AS patient_count,
     CASE WHEN a.description IS NULL
       THEN '4'
     ELSE a.description END                       AS luigi_workers,
     CASE WHEN b.description IS NULL
       THEN '25'
     ELSE b.description END                       AS batch_size,
     CASE WHEN e.description IS NULL
       THEN 'false'
     ELSE e.description END                       AS memory_caching,
     CASE WHEN h.description IS NULL
       THEN 'false'
     ELSE h.description END                       AS precomputed_segmentation,
     CASE WHEN i.description IS NULL
       THEN 'false'
     ELSE i.description END                       AS reordered_nlpql,
     CASE WHEN j.description IS NULL
       THEN 'false'
     ELSE j.description END                       AS chained_queries,
     CASE WHEN k.description IS NULL
       THEN 'false'
     ELSE k.description END                       AS redis_cache,
     l.description                                AS cache_query_count,
     m.description                                AS cache_compute_count,
     n.description                                AS cache_hit_ratio

   FROM (SELECT
           *,
           regexp_split_to_array(name, '_') AS spl
         FROM nlp.nlp_job) AS nj
     LEFT JOIN nlp.nlp_job_status a ON nj.nlp_job_id = a.nlp_job_id AND a.status = 'PROPERTIES_LUIGI_WORKERS'
     LEFT JOIN nlp.nlp_job_status b ON nj.nlp_job_id = b.nlp_job_id AND b.status = 'PROPERTIES_BATCH_SIZE'
     LEFT JOIN nlp.nlp_job_status c ON nj.nlp_job_id = c.nlp_job_id AND c.status = 'STATS_FINAL_RESULTS'
     LEFT JOIN nlp.nlp_job_status d ON nj.nlp_job_id = d.nlp_job_id AND d.status = 'STATS_FINAL_SUBJECTS'
     LEFT JOIN nlp.nlp_job_status e ON nj.nlp_job_id = e.nlp_job_id AND e.status = 'PROPERTIES_USE_MEMORY_CACHING'
     LEFT JOIN nlp.nlp_job_status f ON nj.nlp_job_id = f.nlp_job_id AND f.status = 'STATS_INTERMEDIATE_RESULTS'
     LEFT JOIN nlp.nlp_job_status g ON nj.nlp_job_id = g.nlp_job_id AND g.status = 'STATS_INTERMEDIATE_SUBJECTS'
     LEFT JOIN nlp.nlp_job_status h
       ON nj.nlp_job_id = h.nlp_job_id AND h.status = 'PROPERTIES_USE_PRECOMPUTED_SEGMENTATION'
     LEFT JOIN nlp.nlp_job_status i ON nj.nlp_job_id = i.nlp_job_id AND i.status = 'PROPERTIES_USE_REORDERED_NLPQL'
     LEFT JOIN nlp.nlp_job_status j ON nj.nlp_job_id = j.nlp_job_id AND j.status = 'PROPERTIES_USE_CHAINED_QUERIES'
     LEFT JOIN nlp.nlp_job_status k ON nj.nlp_job_id = k.nlp_job_id AND k.status = 'PROPERTIES_USE_REDIS_CACHING'
     LEFT JOIN nlp.nlp_job_status l ON nj.nlp_job_id = l.nlp_job_id AND l.status = 'STATS_CACHE_QUERY_COUNTS'
     LEFT JOIN nlp.nlp_job_status m ON nj.nlp_job_id = m.nlp_job_id AND m.status = 'STATS_CACHE_COMPUTE_COUNTS'
     LEFT JOIN nlp.nlp_job_status n ON nj.nlp_job_id = n.nlp_job_id AND n.status = 'STATS_CACHE_HIT_RATIO'
   ORDER BY nj.nlp_job_id desc) q1s;


