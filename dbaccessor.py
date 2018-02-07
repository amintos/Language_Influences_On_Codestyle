import psycopg2


class PSQLConn():

    def __init__(self, cfg):
        self._cfg = cfg

    def __enter__(self):
        self.conn = psycopg2.connect(dbname=self._cfg['dbname'],
                                     user=self._cfg['user'],
                                     password=self._cfg['password'],
                                     host=self._cfg['host'],
                                     port=self._cfg['port'])
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


class DBAccessor():

    LANG_PREFIX = {
        'java': 'j',
        'python': 'py',
        'cpp': 'c'
    }
    # Dictionary for all the languages in the joined 'changes_per_author' table
    THRESH_SIGNIFICANCE = 150
    # Significance threshold, see function parameters
    MORE_EXPERIENCE = 5
    # Experience threshold, see function parameters

    def __init__(self, cfg):
        self._cfg = cfg

    def get_candidates(self, primary_lang,
                       second_lang, thresh=THRESH_SIGNIFICANCE,
                       exp=MORE_EXPERIENCE):
        """Get all candidates for the given languages.

        get_candidates('java', 'python', 150, 5) would return you
        a list of candidates, each having the following properties:
            - they all have at least 150 changes in python and java
            - they all have at least 5 times the changes in java than
              in python
            - they have a maximum of 150 changes in other languages
              (per language)

        Args:

        primary_lang: The primary language of the candidate, so the one in
                      which he/she has written most of the code until now.
                      For the evaluation, the candidate will be considered as a
                      '<primary_lang> programmer'.
        second_lang: The secondary language, in which the candidate has still
                     written a significant portion of code and essentially the
                     language we want to test the styles of. For the
                     evaluation, the candidate will be considered as a
                     '<primary_lang> programmer writing <second_lang>'.
        thresh: The significance threshold in LOC, below which the candidate
                will not count as a programmer of that language.
                Defaults to THRESH_SIGNIFICANCE.
        exp: A multiplier describing how much more a candidate has to have
             programmed in his/her primary language than in the second
             language. For example, a multiplier of 5 means that all resulting
             candidates will have programmed at least 5 times more in their
             primary language than in their second language.

        Returns:

        A list of the candidates, each entry consisting of one table row.
        (Usually 'author_id' and the changes for each language.)
        """
        primary_lang2 = [l for l in self.LANG_PREFIX.keys()
                         if l not in (primary_lang, second_lang)]
        if len(primary_lang2) > 1:
            print('Inferring of the second primary language failed.')
            return []
        else:
            primary_lang2 = primary_lang2[0]
        query = ('''SELECT * FROM lics_languages_per_author
                    WHERE {0}changes > {3} AND ({2}changes <= {3} AND
                    {1}changes > {4}*{0}changes);''').format(
            self.LANG_PREFIX[second_lang],
            self.LANG_PREFIX[primary_lang],
            self.LANG_PREFIX[primary_lang2],
            thresh,
            exp)
        result = []
        with PSQLConn(self._cfg) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
        return result

    def get_baseline_programmers(self, lang, min_changes=1000,
                                 thresh=THRESH_SIGNIFICANCE,
                                 result_size=100):
        """Get a certain number of programmers of the given language.

        get_baseline_programmers('python', 1000, 150, 100) would return you
        exactly 100 candidates, each having the following properties:
            - they all have at least 1000 changes in python
            - they have a maximum of 150 changes in other languages
              (per language)

        Args:

        lang: The language for which programmers are needed.
        min_changes: The amount of changes in the given language the programmer
                     should have at least.
        thresh: The significance threshold in LOC, below which the candidate
                will not count as a programmer of that language.
                Defaults to THRESH_SIGNIFICANCE.
        result_size: The maximum amount of programmers to be retrieved.
                     Defaults to 100.

        Returns:

        A list of the programmers, each entry consisting of one table row.
        (Usually 'author_id' and the changes for each language.)
        """
        second_lang, second_lang2 = [l for l in self.LANG_PREFIX.keys()
                                     if l != lang]
        query = '''SELECT * FROM lics_languages_per_author
                    WHERE {0}changes > {3} AND ({1}changes <= {4} AND
                    {2}changes <= {4}) LIMIT {5};'''.format(
            self.LANG_PREFIX[lang],
            self.LANG_PREFIX[second_lang],
            self.LANG_PREFIX[second_lang2],
            min_changes,
            thresh,
            result_size)
        result = []
        with PSQLConn(self._cfg) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
        return result

    def get_projects_for_user(self, user_id, lang=None):
        """Get all the projects for a given user.

        Args:

        user_id: The author_id identifying the author for which
                 to fetch the projects he worked on.
        lang: Optional language restriction for the projects to fetch.
              (e.g. fetch only 'python' projects)

        Returns:

        A list of the projects, each entry consisting of the
        repository url and the project name.
        """
        query = ('''SELECT url, name FROM projects WHERE id IN
                    (SELECT repo_id FROM project_members
                     WHERE user_id =\'{}\')''').format(user_id)
        if lang:
            query += 'AND LOWER(language) LIKE LOWER(\'{}\')'.format(lang)
        result = []
        with PSQLConn(self._cfg) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
        return result
