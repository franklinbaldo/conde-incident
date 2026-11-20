import Conde1963.Core
import Conde1963.CircularMCMC
import Conde1963.HastingsKernel
import Conde1963.OpticalRayVisibility
import Conde1963.OpticalPlateVeto
import Conde1963.NewspaperTemporalCutoff
import Conde1963.TerminalCraterBound
import Conde1963.SharedStateParallax
import Conde1963.SsrSurvivorIntervals
import Conde1963.RelativeTrajectories
import Conde1963.SsrNovember
import Conde1963.UnSsrCrossCompilation
import Conde1963.UnSsrPrintRounding

/-! Audit axiom dependencies of existing documentary results and new
conditional, three-object orbital exclusion theorem. Lean compilation
does not authenticate observed positions or establish a 1963 reentry. -/

#print axioms Conde1963.no_double_count_tupi
#print axioms Conde1963.no_double_count_tracking
#print axioms Conde1963.total_unique_epochs
#print axioms Conde1963.last_528_before_decay
#print axioms Conde1963.frequency_difference_e8
#print axioms Conde1963.joint_model_did_not_beat_quadratic_on_holdout
#print axioms Conde1963.date_alone_does_not_identify_place
#print axioms Conde1963.more_constraints_never_expand
#print axioms Conde1963.RelativeTrajectories.controls_exclude_candidate_if_x_envelopes_disjoint
#print axioms Conde1963.RelativeTrajectories.one_disjoint_epoch_rejects_trajectory

#print axioms Conde1963.SsrNovember.printed_november_period_3c_gt_3a
#print axioms Conde1963.SsrNovember.printed_november_apogee_3c_gt_3a
#print axioms Conde1963.SsrSurvivorIntervals.b_july_to_october_published_difference
#print axioms Conde1963.SsrSurvivorIntervals.c_post_b_november_to_december_published_difference
#print axioms Conde1963.SsrSurvivorIntervals.a_post_b_november_to_december_published_difference
#print axioms Conde1963.SsrSurvivorIntervals.post_b_529_change_exceeds_527_change_in_printed_tables

#print axioms Conde1963.UnSsrCrossCompilation.cross_agency_lower_bound
#print axioms Conde1963.UnSsrCrossCompilation.cross_agency_attaining_witness

#print axioms Conde1963.UnSsrPrintRounding.round_robust_lower_bound
#print axioms Conde1963.UnSsrPrintRounding.rounded_half_step_lower_bound
#print axioms Conde1963.UnSsrPrintRounding.all_26_cells_attain_130
#print axioms Conde1963.UnSsrPrintRounding.half_up_discrete_lower_bound
#print axioms Conde1963.UnSsrPrintRounding.half_even_discrete_lower_bound
#print axioms Conde1963.UnSsrPrintRounding.all_26_strict_interior_attain_131
/-! Exact synthetic circular-MCMC structural audit, not historical inference. -/
#print axioms Conde1963.CircularMCMC.acceptedFlow_detailed_balance
#print axioms Conde1963.CircularMCMC.acceptedFlow_list_balance
#print axioms Conde1963.CircularMCMC.hastingsFlow_detailed_balance
#print axioms Conde1963.CircularMCMC.hastingsFlow_le_forward
#print axioms Conde1963.CircularMCMC.hastingsFlow_maximal
#print axioms Conde1963.CircularMCMC.hastingsFlow_list_balance
#print axioms Conde1963.CircularMCMC.hastingsFlow_asymmetric_example
#print axioms Conde1963.CircularMCMC.asymmetric_proposal_counterexample
#print axioms Conde1963.CircularMCMC.residual_gauge_invariant
#print axioms Conde1963.CircularMCMC.residualVector_gauge_invariant
#print axioms Conde1963.CircularMCMC.likelihood_gauge_invariant
#print axioms Conde1963.CircularMCMC.fixed_bias_can_break_gauge
#print axioms Conde1963.CircularMCMC.unanchored_phase_has_compensator

#print axioms Conde1963.CircularMCMC.calibrated_anchor_identifies_phase_modulo
#print axioms Conde1963.CircularMCMC.calibrated_anchor_rejects_noncongruent_phase

/-! Full finite Hastings mass conservation / stationarity audit (synthetic). -/
#print axioms Conde1963.CircularMCMC.acceptedRow_le_capacity
#print axioms Conde1963.CircularMCMC.fullTransport_row_conservation
#print axioms Conde1963.CircularMCMC.fullTransport_detailed_balance
#print axioms Conde1963.CircularMCMC.fullTransport_stationary
#print axioms Conde1963.CircularMCMC.twoState_rows_equal_four
#print axioms Conde1963.CircularMCMC.twoState_rejections_checked

/-! Conditional ray-occlusion proof, no 1963 observation. -/
#print axioms Conde1963.OpticalRayVisibility.first_earth_entry_excludes_all_larger_ranges
#print axioms Conde1963.OpticalRayVisibility.endpoints_outside_do_not_imply_clear_ray

/-! Exact correlated versus fictitiously independent optical errors (G62). -/
#print axioms Conde1963.SharedStateParallax.covariance_includes_two_cross_terms
#print axioms Conde1963.SharedStateParallax.identical_sensitivities_cancel_shared_noise
#print axioms Conde1963.SharedStateParallax.independence_approximation_changes_result

/-! Conditional negative-plate veto and trailing-loss non-exclusion certificate. -/
#print axioms Conde1963.OpticalPlateVeto.negative_plate_excludes_if_guaranteed
#print axioms Conde1963.OpticalPlateVeto.higher_trailing_loss_cannot_improve_detectability
#print axioms Conde1963.OpticalPlateVeto.non_detection_without_trailing_calibration_does_not_exclude
#print axioms Conde1963.OpticalPlateVeto.bright_object_satisfies_guaranteed_detection

/-! Conditional temporal cutoff from O Globo 1963-11-08/09 primary facsimiles. -/
#print axioms Conde1963.NewspaperTemporalCutoff.causal_report_excludes_later_pass
#print axioms Conde1963.NewspaperTemporalCutoff.oglobo_afternoon_excludes_nov08_evening_528
#print axioms Conde1963.NewspaperTemporalCutoff.morning_528_pass_remains_before_afternoon_cutoff

/-! Conditional work-energy upper bound for 4 m crater excavation by subsonic debris. -/
#print axioms Conde1963.TerminalCraterBound.energy_deficit_excludes_crater_depth
#print axioms Conde1963.TerminalCraterBound.higher_work_threshold_preserves_deficit
#print axioms Conde1963.TerminalCraterBound.hollow_globe_cannot_excavate_4m_crater
#print axioms Conde1963.TerminalCraterBound.dense_agena_fragment_below_4m_overburden_floor
#print axioms Conde1963.TerminalCraterBound.high_energy_impactor_satisfies_4m_bound
