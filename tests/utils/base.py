# ------------------------------------------------
# built-ins
import unittest
# ------------------------------------------------

VALID_CHROMOSOMES = [*[str(chr) for chr in range(23)], 'X', 'Y']
VALID_GWAS_SOURCES = ['GWAS Catalog']
VALID_SNP_ID_REGEX = '^rs\d+$'
VALID_GENE_ID_REGEX = '^ENSG\d+$'
VALID_EFO_ID_REGEX = '^EFO_\d+$'


class TestPostgapBase(unittest.TestCase):
    """
    Base class for postgap tests. Provides common utility methods.
    """

    def __init__(self, test_name, postgap=None):
        super(TestPostgapBase, self).__init__(test_name)
        self.pg = postgap

    def assert_series_against_interval(self, series, low, high, inside=True):
        """
        Check if all values in a `pandas.Series` are inside or outside the range
        [low, high], depending on the value of the inside boolean.
        """
        all_meet_criteria = True
        first_exception = None

        if len(series) > 0:
            between = series.between(low, high)
            meet_criteria = between
            if inside == False:
                meet_criteria = ~between

            all_meet_criteria = meet_criteria.all()
            if (not all_meet_criteria):
                first_exception = series[~meet_criteria].head(1).to_string(index=False)
                first_exception = '{}{} in [{}, {}]'.format(
                    first_exception,
                    ' not' if inside else '',
                    low,
                    high
                )

        self.assertTrue(all_meet_criteria, first_exception)

    def assert_series_in_range(self, series, low, high, allow_na=False):
        """
        Check if all values in a `pandas.Series` are in the range [low, high].
        """
        if allow_na == True:
            self.assert_series_against_interval(series.dropna(), low, high)
        else:
            self.assert_series_against_interval(series, low, high)

    def assert_series_not_in_range(self, series, low, high, allow_na=False):
        """
        Check if all values in a `pandas.Series` are NOT in the range [low, high].
        """
        if allow_na == True:
            self.assert_series_against_interval(series.dropna(), low, high, inside=False)
        else:
            self.assert_series_against_interval(series, low, high, inside=False)

    def assert_series_matches_regex(self, series, regex):
        """
        Check if all values in a `pandas.Series` match a regex.
        """
        match = series.str.match(regex)
        all_match = match.all()
        self.assertTrue(all_match,
                        series[~match].head(1).to_string(index=False))

    def assert_series_valid_gene_id(self, series):
        """
        Check if all values in a `pandas.Series` are valid Ensembl gene ids.
        """
        self.assert_series_matches_regex(series, VALID_GENE_ID_REGEX)

    def assert_series_valid_snp_id(self, series):
        """
        Check if all values in a `pandas.Series` are valid SNP ids.
        """
        self.assert_series_matches_regex(series, VALID_SNP_ID_REGEX)

    def assert_series_valid_efo_id(self, series):
        """
        Check if all values in a `pandas.Series` are valid EFO ids.
        """
        self.assert_series_matches_regex(series, VALID_EFO_ID_REGEX)

    def assert_series_valid_genomic_coord(self, series):
        """
        Check if all values in a `pandas.Series` are valid chromosomal coords.
        """
        self.assertTrue((series > 0).all(),
                        series[series <= 0].head(1))

    def assert_series_valid_chrom(self, series):
        """
        Check if all values in a `pandas.Series` are valid chromosomes.
        """
        series_str = series.apply(str)
        chrs = series_str.unique()
        all_valid = all(chr in VALID_CHROMOSOMES for chr in chrs)
        invalid_freqs = series_str[~series_str.isin(VALID_CHROMOSOMES)].value_counts()
        self.assertTrue(all_valid, invalid_freqs)

    def assert_series_valid_gwas_source(self, series):
        """
        Check if all values in a `pandas.Series` are valid GWAS sources.
        """
        sources = series.unique()
        all_valid = all(s in VALID_GWAS_SOURCES for s in sources)
        invalid_freqs = series[~series.isin(VALID_GWAS_SOURCES)].value_counts()
        self.assertTrue(all_valid, invalid_freqs)


    def assert_groupby_series_is_unique_per_group(self, groupbyseries):
        """
        Check if the `pandas.Series` per group contains a unique value.

        Example:
          `g1=[1, 1, 1], g2=[2, 2]` would pass.
          `g1=[1, 2] g2=[2, 2]` would not pass.
        """
        counts = groupbyseries.nunique()
        counts_are_one = (counts == 1)
        self.assertTrue(counts_are_one.all(),
                        counts[~counts_are_one].head(1))
