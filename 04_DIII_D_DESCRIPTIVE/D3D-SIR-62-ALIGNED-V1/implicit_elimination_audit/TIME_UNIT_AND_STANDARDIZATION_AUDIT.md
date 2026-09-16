# Time-unit and standardization audit

Status: **STANDARDIZED_TEMPORAL_DERIVATIVES_INVARIANT_SHIFTED_RATIOS_REQUIRE_MATCHED_SHIFT_UNITS**

Provider timing is in milliseconds. Finite differences use that `dt`. After per-channel z-scoring, temporal-derivative columns are invariant to a global time-unit rescaling. Additive `shiftval` is applied in the same units as the z-scored derivatives; an unmatched rescaling of derivatives without rescaling `shiftval` changes the shifted ratios and therefore A.
