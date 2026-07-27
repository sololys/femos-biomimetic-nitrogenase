// ====================================================================
// SYSTEMVERILOG HARDWARE CONTRACT: OMNI-GATE PULSE INTERLOCK
// Classification: FAIL-CLOSED ACTUATION GATE (Omega)
// ====================================================================

module omni_gate_latch (
    input  logic        clk,                // Systemklokke (Lab-synkronisert)
    input  logic        rst_n,              // Asynkron aktiv-lav tilbakestilling
    input  logic [15:0] drift_input,        // Real-time D_K verdi fra EKF-estimatoren
    input  logic [15:0] threshold_cfg,      // Konfigurert strukturell barriere (Tau)
    input  logic        rf_pulse_in,        // Rå Gaussisk mikrobølgepuls (Proposal)
    output logic        rf_pulse_out,       // Realisert puls til kryostat-linje
    output logic        interlock_tripped   // HPIS diagnostisk feilpin
);

    logic latch_state;
    logic trip_async;

    // Momentant, asynkront tripp-signal (Kombinatorisk hurtigbane)
    assign trip_async = (drift_input >= threshold_cfg);

    // Deterministisk overvåking og permanent sekvensiell latching
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            latch_state <= 1'b0;
        end else begin
            if (trip_async) begin
                latch_state <= 1'b1;
            end
        end
    end

    // Ultra-lav latens kombinatorisk gating (Både nåtid og minne avskjærer)
    assign interlock_tripped = latch_state | trip_async;
    assign rf_pulse_out      = rf_pulse_in & ~(latch_state | trip_async);

endmodule
