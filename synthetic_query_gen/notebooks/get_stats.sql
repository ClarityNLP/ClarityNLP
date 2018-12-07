select nlp_job_id, name, job_type, job_index, status, date_started, date_ended, extract(HOUR from total_time) * 60 +
                                                                                extract(MINUTE from total_time) as
  total_minutes, extract(SECOND from total_time) total_seconds,
feature_count, patient_count, luigi_workers, batch_size, memory_caching, precomputed_segmentation FROM
(SELECT nj.nlp_job_id, nj.name, nj.spl[1] as job_type, nj.spl[3] as job_index, nj.status, nj.date_started, nj.date_ended,
  ((case when nj.date_ended is null then current_timestamp else nj.date_ended end) - nj.date_started) as total_time,

  case when c.description = '0' then f.description else c.description end as feature_count,
  case when d.description  = '0' then  g.description else d.description end as patient_count,
  a.description as luigi_workers,
  b.description as batch_size,
  e.description as memory_caching,
  h.description as precomputed_segmentation

from (select *, regexp_split_to_array(name, '_') as spl from nlp.nlp_job) as nj
left JOIN nlp.nlp_job_status a on nj.nlp_job_id = a.nlp_job_id and a.status = 'PROPERTIES_LUIGI_WORKERS'
left JOIN nlp.nlp_job_status b on nj.nlp_job_id = b.nlp_job_id and b.status = 'PROPERTIES_BATCH_SIZE'
left JOIN nlp.nlp_job_status c on nj.nlp_job_id = c.nlp_job_id and c.status = 'STATS_FINAL_RESULTS'
left JOIN nlp.nlp_job_status d on nj.nlp_job_id = d.nlp_job_id and d.status = 'STATS_FINAL_SUBJECTS'
left JOIN nlp.nlp_job_status e on nj.nlp_job_id = e.nlp_job_id and e.status = 'PROPERTIES_USE_MEMORY_CACHING'
left JOIN nlp.nlp_job_status f on nj.nlp_job_id = f.nlp_job_id and f.status = 'STATS_INTERMEDIATE_RESULTS'
left JOIN nlp.nlp_job_status g on nj.nlp_job_id = g.nlp_job_id and g.status = 'STATS_INTERMEDIATE_SUBJECTS'
  left JOIN nlp.nlp_job_status h on nj.nlp_job_id = h.nlp_job_id and h.status = 'PROPERTIES_USE_PRECOMPUTED_SEGMENTATION'
order by nj.nlp_job_id) q1;
