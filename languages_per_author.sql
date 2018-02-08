-- Create a table which consists of all the changes for 3 chosen languages (java, python, c++) for each author.
-- Note: Enormous runtime due to frequent access to the raw_patches table.
CREATE TABLE lics_languages_per_author AS
(SELECT author_id, sum(pycommit.changes) as pychanges, sum(jcommit.changes) as jchanges, sum(ccommit.changes) as cchanges FROM

(SELECT author_id, sha
FROM commits) author
JOIN

(SELECT sha, changes FROM raw_patches WHERE name LIKE '%.py') pycommit
ON author.sha = pycommit.sha
JOIN

(SELECT sha, changes FROM raw_patches WHERE name LIKE '%.java') jcommit
ON author.sha = jcommit.sha
JOIN

(SELECT sha, changes FROM raw_patches WHERE name LIKE '%.cpp' OR name LIKE '%.c++' OR name LIKE '%.hpp' OR name LIKE '%.h++') ccommit
ON author.sha = ccommit.sha
GROUP BY author_id);
