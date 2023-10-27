-- SPDX-FileCopyrightText: 2023 Brown, E. M., Nesbitt, A., Hébert-Dufresne, L., Veytsman, B., Pimentel, J. F., Druskat, S., Mietchen, D.
--
-- SPDX-License-Identifier: CC-BY-4.0

#standardSQL
SELECT COUNT(*) as num_downloads, file.project AS project_name
FROM `bigquery-public-data.pypi.file_downloads`
WHERE 
  DATE(timestamp)
    BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    AND CURRENT_DATE()
  AND details.installer.name = 'pip'
GROUP BY file.project
ORDER BY num_downloads DESC

