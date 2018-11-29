SELECT nj.nlp_job_id, nj.name, nj.spl[1] as job_type, nj.spl[3] as job_index, nj.status, nj.date_started, nj.date_ended,
  case when nj.date_ended is not null then EXTRACT(MINUTE from (nj.date_ended - nj.date_started)) else 0 end as total_minutes,
  c.description as result_feature_count,
  d.description as result_patient_count,
  a.description as luigi_workers,
  b.description as batch_size,
  e.description as memory_caching

from (select *, regexp_split_to_array(name, '_') as spl from nlp.nlp_job) as nj
left JOIN nlp.nlp_job_status a on nj.nlp_job_id = a.nlp_job_id and a.status = 'PROPERTIES_LUIGI_WORKERS'
left JOIN nlp.nlp_job_status b on nj.nlp_job_id = b.nlp_job_id and b.status = 'PROPERTIES_BATCH_SIZE'
left JOIN nlp.nlp_job_status c on nj.nlp_job_id = c.nlp_job_id and c.status = 'STATS_FINAL_RESULTS'
left JOIN nlp.nlp_job_status d on nj.nlp_job_id = d.nlp_job_id and d.status = 'STATS_FINAL_SUBJECTS'
left JOIN nlp.nlp_job_status e on nj.nlp_job_id = e.nlp_job_id and e.status = 'PROPERTIES_USE_MEMORY_CACHING'
order by nj.nlp_job_id;
