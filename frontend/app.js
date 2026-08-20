/* ============================================================
   AUTOFUZZLLM — FRONTEND CONTROLLER
============================================================ */

"use strict";


/* ============================================================
   STATE
============================================================ */

const AppState = {

    running: false,

    startedAt: null,

    timer: null,

    data: {

        planned: 0,

        executed: 0,

        failed: 0,

        averageRisk: 0,

        averageLVI: 0,

        highestLVI: 0,

        lowestLVI: 0,

        criticalLVI: 0,

        safe: 0,

        warning: 0,

        critical: 0,

        attacks: {},

        models: []

    }

};


/* ============================================================
   HELPERS
============================================================ */

const $ = (id) =>
    document.getElementById(id);


function safeNumber(value, fallback = 0) {

    const number = Number(value);

    return Number.isFinite(number)
        ? number
        : fallback;
}


function formatNumber(value, decimals = 1) {

    const number = safeNumber(value);

    return number
        .toFixed(decimals)
        .replace(/\.0+$/, "");
}


/* ============================================================
   INITIALIZE
============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    initialize
);


function initialize() {

    setupNavigation();

    setupClock();

    setupCursor();

    setupSliders();

    setupSeedSource();

    setupProviders();

    setupLaunchButton();

    resetDashboard();

    console.log(
        "[AutoFuzzLLM] Security console initialized."
    );
}


/* ============================================================
   CLOCK
============================================================ */

function setupClock() {

    const clock = $("clock");

    if (!clock) {
        return;
    }


    function updateClock() {

        const now = new Date();

        clock.textContent =
            now.toLocaleTimeString(
                [],
                {
                    hour12: false
                }
            );

    }


    updateClock();

    setInterval(
        updateClock,
        1000
    );
}


/* ============================================================
   CURSOR GLOW
============================================================ */

function setupCursor() {

    const glow =
        $("cursor-glow");

    if (!glow) {
        return;
    }


    document.addEventListener(
        "mousemove",
        event => {

            glow.style.left =
                `${event.clientX}px`;

            glow.style.top =
                `${event.clientY}px`;

        }
    );

}


/* ============================================================
   NAVIGATION
============================================================ */

function setupNavigation() {

    const items =
        document.querySelectorAll(
            ".nav-item"
        );


    items.forEach(
        item => {

            item.addEventListener(
                "click",
                () => {

                    const section =
                        item.dataset.section;

                    showSection(
                        section
                    );

                }
            );

        }
    );

}


function showSection(section) {

    document
        .querySelectorAll(".page-section")
        .forEach(
            element => {

                element.classList.remove(
                    "active-section"
                );

            }
        );


    document
        .querySelectorAll(".nav-item")
        .forEach(
            element => {

                element.classList.toggle(
                    "active",
                    element.dataset.section
                    === section
                );

            }
        );


    const target =
        $(`${section}-section`);


    if (target) {

        target.classList.add(
            "active-section"
        );

    }


    const titles = {

        campaign:
            "Evolutionary Campaign",

        live:
            "Live Test",

        analytics:
            "Security Analytics",

        history:
            "Campaign History"

    };


    const title =
        $("page-title");


    if (title) {

        title.textContent =
            titles[section]
            || "AutoFuzzLLM";

    }

}


/* ============================================================
   SLIDERS
============================================================ */

function setupSliders() {

    bindSlider(
        "mutations",
        "mutation-value"
    );

    bindSlider(
        "generations",
        "generation-value"
    );

    bindSlider(
        "initial-seed-count",
        "initial-seed-value"
    );

    bindSlider(
        "seed-pool-size",
        "pool-value"
    );

    bindSlider(
        "fitness-threshold",
        "fitness-value"
    );

}


function bindSlider(
    inputId,
    outputId
) {

    const input =
        $(inputId);

    const output =
        $(outputId);


    if (!input || !output) {
        return;
    }


    function update() {

        output.textContent =
            input.value;

    }


    input.addEventListener(
        "input",
        update
    );


    update();

}


/* ============================================================
   PROVIDERS
============================================================ */

function setupProviders() {

    const providers =
        document.querySelectorAll(
            'input[name="provider"]'
        );


    providers.forEach(
        input => {

            input.addEventListener(
                "change",
                updateProviderCount
            );

        }
    );


    updateProviderCount();

}


function updateProviderCount() {

    const count =
        document.querySelectorAll(
            'input[name="provider"]:checked'
        ).length;


    const element =
        $("provider-count");


    if (element) {

        element.textContent =
            count;

    }

}


/* ============================================================
   SEED SOURCE
============================================================ */

function setupSeedSource() {

    const select =
        $("seed-source");

    const datasetGroup =
        $("dataset-group");

    const promptGroup =
        $("custom-prompt-group");

    const initialSeedGroup =
        $("initial-seed-group");


    if (!select) {

        return;

    }


    const update = () => {

        const source =
            select.value;


        const isBuiltIn =
            source === "Built-in Dataset";

        const isCustom =
            source === "Custom Prompt";

        const isHybrid =
            source === "Hybrid Mode";


        /*
         * DATASET
         *
         * Built-in  -> visible
         * Custom    -> hidden
         * Hybrid    -> visible
         */

        if (datasetGroup) {

            datasetGroup.classList.toggle(
                "hidden",
                isCustom
            );

        }


        /*
         * CUSTOM PROMPT
         *
         * Built-in  -> hidden
         * Custom    -> visible
         * Hybrid    -> visible
         */

        if (promptGroup) {

            promptGroup.classList.toggle(
                "hidden",
                isBuiltIn
            );

        }


        /*
         * INITIAL SEED COUNT
         *
         * Built-in  -> visible
         * Custom    -> hidden
         * Hybrid    -> visible
         */

        if (initialSeedGroup) {

            initialSeedGroup.classList.toggle(
                "hidden",
                isCustom
            );

        }

    };


    select.addEventListener(
        "change",
        update
    );


    update();

}


/* ============================================================
   CONFIGURATION
============================================================ */

function collectConfiguration() {

    const providers =
        Array.from(
            document.querySelectorAll(
                'input[name="provider"]:checked'
            )
        ).map(
            input => input.value
        );


    const seedSource =
        $("seed-source")?.value
        || "Built-in Dataset";


    return {

        providers,

        seed_source:
            seedSource,

        dataset_name:
            $("dataset")?.value
            || null,

        custom_prompt:
            $("custom-prompt")?.value
            || "",

        initial_seed_count:
            safeNumber(
                $("initial-seed-count")?.value
            ),

        mutations:
            safeNumber(
                $("mutations")?.value,
                5
            ),

        generations:
            safeNumber(
                $("generations")?.value,
                3
            ),

        seed_pool_size:
            safeNumber(
                $("seed-pool-size")?.value,
                100
            ),

        fitness_threshold:
            safeNumber(
                $("fitness-threshold")?.value,
                30
            )

    };

}


/* ============================================================
   VALIDATION
============================================================ */

function validateConfiguration(
    configuration
) {

    if (
        !configuration.providers.length
    ) {

        showToast(
            "Select at least one LLM provider.",
            "warning"
        );

        return false;
    }


    if (
        configuration.seed_source
        === "Custom Prompt"
        &&
        !configuration.custom_prompt.trim()
    ) {

        showToast(
            "Enter a custom seed prompt.",
            "warning"
        );

        return false;
    }


    return true;

}


/* ============================================================
   LAUNCH BUTTON
============================================================ */

function setupLaunchButton() {

    const button =
        $("launch-button");


    if (!button) {
        return;
    }


    button.addEventListener(
        "click",
        launchCampaign
    );

}


/* ============================================================
   LAUNCH CAMPAIGN
============================================================ */

async function launchCampaign() {

    if (AppState.running) {
        return;
    }


    const configuration =
        collectConfiguration();


    if (
        !validateConfiguration(
            configuration
        )
    ) {

        return;

    }


    resetDashboard();

    setCampaignRunning(
        true
    );


    updateExecutionStatus(
        "Preparing fuzzing campaign..."
    );


    try {

        const response =
            await fetch(
                "/api/campaign/run",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify(
                            configuration
                        )

                }
            );


        if (!response.ok) {

            let message =
                `HTTP ${response.status}`;

            try {

                const errorData =
                    await response.json();

                message =
                    errorData.detail
                    || errorData.message
                    || message;

            }
            catch (_) {
                // Ignore JSON parsing failure.
            }


            throw new Error(
                message
            );

        }


        updateExecutionStatus(
            "Processing campaign results..."
        );


        const payload =
            await response.json();


        const result =
            payload.data
            || payload;


        applyCampaignResult(
            result
        );


        updateExecutionStatus(
            "Campaign completed successfully."
        );


        showToast(
            "Security campaign completed.",
            "success"
        );

    }
    catch (error) {

        console.error(
            "[AutoFuzzLLM]",
            error
        );


        updateExecutionStatus(
            `Campaign failed: ${error.message}`
        );


        showToast(
            "Campaign failed. Check the FastAPI terminal.",
            "error"
        );

    }
    finally {

        setCampaignRunning(
            false
        );

    }

}


/* ============================================================
   RUNNING STATE
============================================================ */

function setCampaignRunning(
    running
) {

    AppState.running =
        running;


    const button =
        $("launch-button");


    if (button) {

        button.disabled =
            running;


        button.classList.toggle(
            "running",
            running
        );


        if (running) {

            button.innerHTML = `
                <span class="launch-icon">●</span>
                <span class="launch-text">
                    Campaign running...
                </span>
                <span class="launch-shortcut mono">
                    PROCESSING
                </span>
            `;

        }
        else {

            button.innerHTML = `
                <span class="launch-icon">→</span>
                <span class="launch-text">
                    Launch security campaign
                </span>
                <span class="launch-shortcut mono">
                    ENTER
                </span>
            `;

        }

    }


    const panel =
        $("execution-panel");


    if (panel) {

        panel.classList.toggle(
            "hidden",
            !running
        );

    }


    if (running) {

        AppState.startedAt =
            Date.now();

        startTimer();

    }
    else {

        stopTimer();

    }

}


/* ============================================================
   TIMER
============================================================ */

function startTimer() {

    stopTimer();


    function update() {

        if (!AppState.startedAt) {
            return;
        }


        const elapsed =
            (
                Date.now()
                -
                AppState.startedAt
            ) / 1000;


        const element =
            $("elapsed-time");


        if (element) {

            element.textContent =
                `${elapsed.toFixed(1)}s`;

        }

    }


    update();


    AppState.timer =
        setInterval(
            update,
            100
        );

}


function stopTimer() {

    if (AppState.timer) {

        clearInterval(
            AppState.timer
        );

        AppState.timer =
            null;

    }

}


/* ============================================================
   EXECUTION STATUS
============================================================ */

function updateExecutionStatus(
    message
) {

    const element =
        $("execution-status");


    if (element) {

        element.textContent =
            message;

    }

}


/* ============================================================
   PROGRESS
============================================================ */

function updateProgress(
    completed,
    planned
) {

    const bar =
        $("progress-bar");

    const percent =
        $("execution-percent");


    if (!bar) {
        return;
    }


    if (
        !planned
        ||
        planned <= 0
    ) {

        bar.style.width =
            "8%";

        if (percent) {
            percent.textContent =
                "RUNNING";
        }

        return;

    }


    const value =
        Math.min(
            100,
            Math.max(
                0,
                (
                    completed
                    /
                    planned
                ) * 100
            )
        );


    bar.style.width =
        `${value}%`;


    if (percent) {

        percent.textContent =
            `${Math.round(value)}%`;

    }

}


/* ============================================================
   RESET DASHBOARD
============================================================ */

function resetDashboard() {

    AppState.data = {

        planned: 0,

        executed: 0,

        failed: 0,

        averageRisk: 0,

        averageLVI: 0,

        highestLVI: 0,

        lowestLVI: 0,

        criticalLVI: 0,

        safe: 0,

        warning: 0,

        critical: 0,

        attacks: {},

        models: []

    };


    renderMetrics(
        AppState.data
    );


    renderLVI(
        AppState.data
    );


    renderSeverity(
        AppState.data
    );


    renderThreatChart(
        AppState.data
    );


    renderAttackDistribution(
        {}
    );


    renderModels(
        []
    );


    updateProgress(
        0,
        0
    );

}


/* ============================================================
   BACKEND RESULT
============================================================ */

function applyCampaignResult(
    result
) {

    if (
        !result
        ||
        typeof result !== "object"
    ) {

        throw new Error(
            "Invalid campaign response."
        );

    }


    const data = {

        planned:
            safeNumber(
                result.planned
                ??
                result.estimated
                ??
                result.tests
                ??
                result.total_tests
            ),

        executed:
            safeNumber(
                result.executed
                ??
                result.executed_tests
            ),

        failed:
            safeNumber(
                result.failed
                ??
                result.failed_tests
            ),

        averageRisk:
            safeNumber(
                result.average_risk
                ??
                result.averageRisk
                ??
                result.average
            ),

        averageLVI:
            safeNumber(
                result.average_lvi
                ??
                result.averageLVI
            ),

        highestLVI:
            safeNumber(
                result.highest_lvi
                ??
                result.highestLVI
            ),

        lowestLVI:
            safeNumber(
                result.lowest_lvi
                ??
                result.lowestLVI
            ),

        criticalLVI:
            safeNumber(
                result.critical_lvi
                ??
                result.criticalLVI
            ),

        safe:
            safeNumber(
                result.safe
            ),

        warning:
            safeNumber(
                result.warning
            ),

        critical:
            safeNumber(
                result.critical
            ),

        attacks:
            result.attack_distribution
            ||
            result.attacks
            ||
            {},

        models:
            result.provider_comparison
            ||
            result.models
            ||
            []

    };


    AppState.data =
        data;


    renderMetrics(
        data
    );


    renderLVI(
        data
    );


    renderSeverity(
        data
    );


    renderThreatChart(
        data
    );


    renderAttackDistribution(
        data.attacks
    );


    renderModels(
        data.models
    );


    updateProgress(
        data.executed,
        data.planned
    );

}


/* ============================================================
   METRICS
============================================================ */

function renderMetrics(
    data
) {

    animateValue(
        "planned-tests",
        data.planned
    );


    animateValue(
        "executed-tests",
        data.executed
    );


    animateValue(
        "failed-tests",
        data.failed
    );


    animateValue(
        "average-risk",
        data.averageRisk,
        1
    );

}


/* ============================================================
   ANIMATED NUMBERS
============================================================ */

function animateValue(
    id,
    target,
    decimals = 0
) {

    const element =
        $(id);


    if (!element) {
        return;
    }


    const start =
        safeNumber(
            element.dataset.value,
            0
        );


    const end =
        safeNumber(
            target,
            0
        );


    element.dataset.value =
        end;


    const duration =
        600;


    const started =
        performance.now();


    function frame(now) {

        const progress =
            Math.min(
                1,
                (
                    now
                    -
                    started
                )
                /
                duration
            );


        const eased =
            1 -
            Math.pow(
                1 - progress,
                3
            );


        const value =
            start
            +
            (
                end
                -
                start
            )
            *
            eased;


        element.textContent =
            decimals
                ? value.toFixed(decimals)
                : Math.round(value);


        if (progress < 1) {

            requestAnimationFrame(
                frame
            );

        }

    }


    requestAnimationFrame(
        frame
    );


    const metric =
        element.closest(
            ".metric"
        );


    if (metric) {

        metric.classList.remove(
            "animate"
        );


        void metric.offsetWidth;


        metric.classList.add(
            "animate"
        );

    }

}


/* ============================================================
   LVI
============================================================ */

function renderLVI(
    data
) {

    animateValue(
        "average-lvi",
        data.averageLVI,
        1
    );


    animateValue(
        "highest-lvi",
        data.highestLVI,
        1
    );


    animateValue(
        "lowest-lvi",
        data.lowestLVI,
        1
    );


    animateValue(
        "critical-lvi",
        data.criticalLVI
    );


    const progress =
        $("lvi-progress");


    if (progress) {

        const value =
            Math.min(
                100,
                Math.max(
                    0,
                    data.averageLVI
                )
            );


        progress.style.width =
            `${value}%`;

    }

}


/* ============================================================
   SEVERITY
============================================================ */

function renderSeverity(
    data
) {

    animateValue(
        "safe-count",
        data.safe
    );


    animateValue(
        "warning-count",
        data.warning
    );


    animateValue(
        "critical-count",
        data.critical
    );

}


/* ============================================================
   THREAT CHART
============================================================ */

function renderThreatChart(
    data
) {

    const total =
        data.safe
        +
        data.warning
        +
        data.critical;


    if (!total) {

        setBar(
            "safe-bar",
            0
        );

        setBar(
            "warning-bar",
            0
        );

        setBar(
            "critical-bar",
            0
        );

        return;

    }


    setBar(
        "safe-bar",
        (
            data.safe
            /
            total
        ) * 100
    );


    setBar(
        "warning-bar",
        (
            data.warning
            /
            total
        ) * 100
    );


    setBar(
        "critical-bar",
        (
            data.critical
            /
            total
        ) * 100
    );

}


function setBar(
    id,
    value
) {

    const element =
        $(id);


    if (!element) {
        return;
    }


    element.style.height =
        `${Math.max(2, value)}%`;

}


/* ============================================================
   ATTACK DISTRIBUTION
============================================================ */

function renderAttackDistribution(
    attacks
) {

    const container =
        $("attack-distribution");


    if (!container) {
        return;
    }


    const entries =
        Object.entries(
            attacks || {}
        )
        .sort(
            (a,b) => b[1] - a[1]
        );


    if (!entries.length) {

        container.innerHTML = `
            <div class="empty-state">
                No campaign data yet.
            </div>
        `;

        return;

    }


    const max =
        Math.max(
            ...entries.map(
                item => safeNumber(item[1])
            )
        );


    container.innerHTML =
        entries
            .map(
                ([name,count]) => {

                    const value =
                        safeNumber(count);


                    const width =
                        max
                            ? (
                                value
                                /
                                max
                            ) * 100
                            : 0;


                    return `
                        <div class="attack-row">

                            <span class="attack-name">
                                ${escapeHTML(name)}
                            </span>

                            <div class="attack-right">

                                <div class="attack-bar">

                                    <span
                                        style="width:${width}%"
                                    ></span>

                                </div>

                                <span class="attack-count">
                                    ${value}
                                </span>

                            </div>

                        </div>
                    `;

                }
            )
            .join("");

}


/* ============================================================
   MODEL COMPARISON
============================================================ */

function renderModels(
    models
) {

    const container =
        $("model-comparison");


    if (!container) {
        return;
    }


    if (
        !Array.isArray(models)
        ||
        !models.length
    ) {

        container.innerHTML = `
            <div class="empty-state">
                Run a campaign to compare model resilience.
            </div>
        `;

        return;

    }


    container.innerHTML = `

        <div class="model-header">

            <span>PROVIDER</span>
            <span>TESTS</span>
            <span>AVG RISK</span>
            <span>AVG LVI</span>
            <span>CRITICAL</span>
            <span>WARNING</span>
            <span>SAFE</span>

        </div>

        ${
            models
                .map(
                    model => `

                        <div class="model-row">

                            <span class="model-provider">
                                ${escapeHTML(
                                    model.provider
                                    || "Unknown"
                                )}
                            </span>

                            <span>
                                ${safeNumber(
                                    model.tests
                                )}
                            </span>

                            <span>
                                ${formatNumber(
                                    model.average_risk,
                                    1
                                )}
                            </span>

                            <span>
                                ${formatNumber(
                                    model.average_lvi,
                                    1
                                )}
                            </span>

                            <span class="model-critical">
                                ${safeNumber(
                                    model.critical
                                )}
                            </span>

                            <span class="model-warning">
                                ${safeNumber(
                                    model.warning
                                )}
                            </span>

                            <span class="model-safe">
                                ${safeNumber(
                                    model.safe
                                )}
                            </span>

                        </div>

                    `
                )
                .join("")
        }

    `;

}


/* ============================================================
   TOAST
============================================================ */

function showToast(
    message,
    type = "info"
) {

    let container =
        document.getElementById(
            "toast-container"
        );


    if (!container) {

        container =
            document.createElement(
                "div"
            );


        container.id =
            "toast-container";


        Object.assign(
            container.style,
            {

                position: "fixed",

                right: "22px",

                bottom: "22px",

                zIndex: "1000",

                display: "flex",

                flexDirection: "column",

                gap: "8px"

            }
        );


        document.body.appendChild(
            container
        );

    }


    const toast =
        document.createElement(
            "div"
        );


    const colors = {

        success:
            "rgba(113,227,155,.9)",

        warning:
            "rgba(255,200,87,.9)",

        error:
            "rgba(255,93,104,.9)",

        info:
            "rgba(100,229,255,.9)"

    };


    Object.assign(
        toast.style,
        {

            padding:
                "11px 14px",

            border:
                `1px solid ${colors[type] || colors.info}`,

            borderRadius:
                "9px",

            background:
                "rgba(10,13,18,.95)",

            color:
                "#e8ebee",

            fontFamily:
                "Inter, sans-serif",

            fontSize:
                "10px",

            boxShadow:
                "0 15px 40px rgba(0,0,0,.35)",

            backdropFilter:
                "blur(12px)",

            animation:
                "sectionIn .25s ease"

        }
    );


    toast.textContent =
        message;


    container.appendChild(
        toast
    );


    setTimeout(
        () => {

            toast.style.opacity =
                "0";

            toast.style.transform =
                "translateY(6px)";

            toast.style.transition =
                "all .25s ease";


            setTimeout(
                () => toast.remove(),
                260
            );

        },
        3200
    );

}


/* ============================================================
   HTML ESCAPE
============================================================ */

function escapeHTML(
    value
) {

    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );

}


/* ============================================================
   KEYBOARD SHORTCUT
============================================================ */

document.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter"
            &&
            !event.shiftKey
            &&
            document.activeElement.tagName
            !== "TEXTAREA"
            &&
            !AppState.running
        ) {

            const button =
                $("launch-button");


            if (
                button
                &&
                !button.disabled
            ) {

                launchCampaign();

            }

        }

    }
);