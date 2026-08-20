/* ============================================================
   AUTOFUZZLLM FRONTEND CONTROLLER

   Responsibilities:
   - Sidebar navigation
   - Sliders
   - Seed configuration
   - Campaign UI
   - Initial zero state
   - Campaign API communication
   - Metrics rendering
   - Model comparison rendering
   - Live background animation state
============================================================ */

"use strict";


/* ============================================================
   APPLICATION STATE
============================================================ */

const AppState = {

    running: false,

    campaignStartedAt: null,

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
   DOM HELPER
============================================================ */

function $(id) {

    const element = document.getElementById(id);

    if (!element) {

        console.warn(
            `[AutoFuzzLLM] Element not found: ${id}`
        );

    }

    return element;
}


/* ============================================================
   SAFE NUMBER
============================================================ */

function safeNumber(value, fallback = 0) {

    const number = Number(value);

    return Number.isFinite(number)
        ? number
        : fallback;
}


/* ============================================================
   FORMAT NUMBER
============================================================ */

function formatNumber(value, decimals = 1) {

    const number = safeNumber(value);

    return number.toFixed(decimals)
        .replace(/\.0+$/, "");
}


/* ============================================================
   INITIALIZATION
============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    initializeApplication
);


function initializeApplication() {

    console.log(
        "[AutoFuzzLLM] Frontend initialized."
    );

    setupNavigation();

    setupSliders();

    setupSeedSource();

    setupCampaignButton();

    setupChat();

    /*
     * IMPORTANT:
     * Start with ZERO values.
     * We do NOT put fake previous campaign numbers
     * into the interface.
     */
    resetDashboard();

    /*
     * Build model area as empty initially.
     */
    renderModels([]);

}


/* ============================================================
   NAVIGATION
============================================================ */

function setupNavigation() {

    const navigationItems =
        document.querySelectorAll(
            ".nav-item"
        );

    navigationItems.forEach(
        (button) => {

            button.addEventListener(
                "click",
                () => {

                    const section =
                        button.dataset.section;

                    if (!section) {

                        return;

                    }

                    showSection(section);

                }
            );

        }
    );

}


function showSection(section) {

    const sections =
        document.querySelectorAll(
            ".page-section"
        );

    sections.forEach(
        (item) => {

            item.classList.remove(
                "active-section"
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


    const navigationItems =
        document.querySelectorAll(
            ".nav-item"
        );

    navigationItems.forEach(
        (button) => {

            button.classList.toggle(
                "active",
                button.dataset.section === section
            );

        }
    );


    const title = $("page-title");

    if (!title) {

        return;

    }


    const titles = {

        campaign:
            "Evolutionary Campaign",

        live:
            "Conversation Fuzzer",

        analytics:
            "Security Analytics",

        history:
            "Campaign History"

    };


    title.textContent =
        titles[section]
        || "AutoFuzzLLM";

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

    const input = $(inputId);

    const output = $(outputId);

    if (!input || !output) {

        return;

    }


    const update = () => {

        output.textContent =
            input.value;

    };


    input.addEventListener(
        "input",
        update
    );

    update();

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


    if (!select) {

        return;

    }


    const update = () => {

        const source =
            select.value;

        const custom =
            source === "Custom Prompt";


        if (datasetGroup) {

            datasetGroup.classList.toggle(
                "hidden",
                custom
            );

        }


        if (promptGroup) {

            promptGroup.classList.toggle(
                "hidden",
                !custom
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
   CAMPAIGN BUTTON
============================================================ */

function setupCampaignButton() {

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
   COLLECT CONFIGURATION
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


    const configuration = {

        providers,

        seed_source:
            seedSource,

        dataset:
            $("dataset")?.value
            || null,

        custom_prompt:
            $("custom-prompt")?.value
            || "",

        mutations:
            safeNumber(
                $("mutations")?.value
            ),

        generations:
            safeNumber(
                $("generations")?.value
            ),

        seed_pool_size:
            safeNumber(
                $("seed-pool-size")?.value
            ),

        fitness_threshold:
            safeNumber(
                $("fitness-threshold")?.value
            )

    };


    return configuration;

}


/* ============================================================
   CAMPAIGN VALIDATION
============================================================ */

function validateConfiguration(
    configuration
) {

    if (
        !configuration.providers ||
        configuration.providers.length === 0
    ) {

        alert(
            "Please select at least one LLM provider."
        );

        return false;

    }


    if (
        configuration.seed_source ===
        "Custom Prompt" &&
        !configuration.custom_prompt.trim()
    ) {

        alert(
            "Please enter a custom seed prompt."
        );

        return false;

    }


    return true;

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


    setCampaignRunning(true);

    resetDashboard();

    updateExecutionStatus(
        "Initializing Threat Assessment Matrix..."
    );


    try {

        /*
         * The frontend talks to FastAPI.
         *
         * IMPORTANT:
         * This endpoint must exist in server.py.
         */

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

            throw new Error(
                `Campaign API returned HTTP ${response.status}`
            );

        }


        const result =
            await response.json();


        /*
         * The backend may return:
         *
         * {
         *   success: true,
         *   data: {...}
         * }
         *
         * OR directly {...}
         */

        const campaignData =
            result.data
            || result;


        applyCampaignResult(
            campaignData
        );


        updateExecutionStatus(
            "Campaign completed successfully."
        );


    }
    catch (error) {

        console.error(
            "[AutoFuzzLLM] Campaign error:",
            error
        );


        updateExecutionStatus(
            `Campaign failed: ${error.message}`
        );


        /*
         * Failed API communication should NOT
         * create fake statistics.
         */

        setCampaignError();

    }
    finally {

        setCampaignRunning(false);

    }

}


/* ============================================================
   CAMPAIGN RUNNING STATE
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


        button.innerHTML =
            running
                ? "<span>⏳</span> Campaign Running..."
                : "<span>🚀</span> Launch Evolutionary Campaign";

    }


    const executionPanel =
        $("execution-panel");


    if (executionPanel) {

        executionPanel.classList.toggle(
            "hidden",
            !running
        );

    }


    document.body.classList.toggle(
        "campaign-running",
        running
    );


    if (running) {

        AppState.campaignStartedAt =
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


    const update = () => {

        if (
            !AppState.campaignStartedAt
        ) {

            return;

        }


        const elapsed =
            (
                Date.now() -
                AppState.campaignStartedAt
            ) / 1000;


        const element =
            $("elapsed-time");


        if (element) {

            element.textContent =
                `${elapsed.toFixed(1)}s`;

        }

    };


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

    const status =
        $("execution-status");


    if (status) {

        status.textContent =
            message;

    }

}


/* ============================================================
   ERROR STATE
============================================================ */

function setCampaignError() {

    updateExecutionStatus(
        "Campaign could not be completed. Check the FastAPI terminal."
    );

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


    if (!bar) {

        return;

    }


    const total =
        safeNumber(
            planned
        );


    const done =
        safeNumber(
            completed
        );


    if (total <= 0) {

        bar.style.width =
            "0%";

        return;

    }


    const percentage =
        Math.min(
            100,
            Math.max(
                0,
                (done / total) * 100
            )
        );


    bar.style.width =
        `${percentage}%`;

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

    renderAttackDistribution(
        {}
    );

    renderModels(
        []
    );

    updateLVI(
        AppState.data
    );

    updateProgress(
        0,
        0
    );

}


/* ============================================================
   APPLY BACKEND RESULT
============================================================ */

function applyCampaignResult(
    result
) {

    if (
        !result ||
        typeof result !== "object"
    ) {

        throw new Error(
            "Backend returned invalid campaign data."
        );

    }


    /*
     * Supports both backend naming styles.
     */

    const data = {

        planned:
            safeNumber(
                result.planned
                ?? result.tests
                ?? result.total_tests
            ),

        executed:
            safeNumber(
                result.executed
                ?? result.executed_tests
            ),

        failed:
            safeNumber(
                result.failed
                ?? result.failed_tests
            ),

        averageRisk:
            safeNumber(
                result.averageRisk
                ?? result.average
                ?? result.average_risk
            ),

        averageLVI:
            safeNumber(
                result.averageLVI
                ?? result.average_lvi
            ),

        highestLVI:
            safeNumber(
                result.highestLVI
                ?? result.highest_lvi
            ),

        lowestLVI:
            safeNumber(
                result.lowestLVI
                ?? result.lowest_lvi
            ),

        criticalLVI:
            safeNumber(
                result.criticalLVI
                ?? result.critical_lvi
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
            result.attacks
            || result.attack_summary
            || {},

        models:
            result.models
            || []

    };


    AppState.data =
        data;


    renderMetrics(
        data
    );


    renderAttackDistribution(
        data.attacks
    );


    renderModels(
        data.models
    );


    updateLVI(
        data
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

    setText(
        "planned-tests",
        formatNumber(data.planned, 0)
    );

    setText(
        "executed-tests",
        formatNumber(data.executed, 0)
    );

    setText(
        "failed-tests",
        formatNumber(data.failed, 0)
    );

    setText(
        "average-risk",
        formatNumber(data.averageRisk, 1)
    );

    setText(
        "average-lvi",
        formatNumber(data.averageLVI, 1)
    );

    setText(
        "highest-lvi",
        formatNumber(data.highestLVI, 1)
    );

    setText(
        "lowest-lvi",
        formatNumber(data.lowestLVI, 1)
    );

    setText(
        "critical-lvi",
        formatNumber(data.criticalLVI, 0)
    );

    setText(
        "safe-count",
        formatNumber(data.safe, 0)
    );

    setText(
        "warning-count",
        formatNumber(data.warning, 0)
    );

    setText(
        "critical-count",
        formatNumber(data.critical, 0)
    );

}


function setText(
    id,
    value
) {

    const element =
        $(id);

    if (element) {

        element.textContent =
            value;

    }

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
        );


    const defaultCategories = [

        "Prompt Injection",

        "Jailbreak",

        "Prompt Leakage",

        "Policy Violation"

    ];


    const values =
        entries.length > 0
            ? entries
            : defaultCategories.map(
                name => [name, 0]
            );


    container.innerHTML =
        "";


    values.forEach(
        ([name, value]) => {

            const row =
                document.createElement(
                    "div"
                );


            const label =
                document.createElement(
                    "span"
                );


            const count =
                document.createElement(
                    "strong"
                );


            label.textContent =
                name;


            count.textContent =
                formatNumber(
                    value,
                    0
                );


            row.appendChild(
                label
            );

            row.appendChild(
                count
            );


            container.appendChild(
                row
            );

        }
    );

}


/* ============================================================
   LVI
============================================================ */

function updateLVI(
    data
) {

    const value =
        safeNumber(
            data.averageLVI
        );


    setText(
        "lvi-main-value",
        formatNumber(value, 1)
    );


    const status =
        $("lvi-status");


    if (!status) {

        return;

    }


    if (
        data.executed === 0
    ) {

        status.textContent =
            "Awaiting campaign";

        return;

    }


    if (value >= 80) {

        status.textContent =
            "Critical vulnerability level";

    }
    else if (value >= 50) {

        status.textContent =
            "High vulnerability level";

    }
    else if (value >= 30) {

        status.textContent =
            "Moderate vulnerability level";

    }
    else {

        status.textContent =
            "Low vulnerability level";

    }

}


/* ============================================================
   MODEL CARDS
============================================================ */

function renderModels(
    models
) {

    const container =
        $("model-cards");


    if (!container) {

        return;

    }


    container.innerHTML =
        "";


    if (
        !Array.isArray(models)
        || models.length === 0
    ) {

        container.innerHTML = `

            <div class="model-card">

                <div class="model-header">

                    <div class="model-avatar">
                        —
                    </div>

                    <div>

                        <strong>
                            No campaign data
                        </strong>

                        <small>
                            Run a campaign to compare models
                        </small>

                    </div>

                </div>

                <div class="model-stats">

                    <div>
                        <span>Average Risk</span>
                        <strong>0</strong>
                    </div>

                    <div>
                        <span>Critical</span>
                        <strong>0</strong>
                    </div>

                </div>

            </div>

        `;

        return;

    }


    models.forEach(
        model => {

            const name =
                typeof model === "string"
                    ? model
                    : model.provider
                    || model.Provider
                    || "Unknown";


            const risk =
                typeof model === "object"
                    ? safeNumber(
                        model.averageRisk
                        ?? model.Average_Risk
                        ?? model.average_risk
                    )
                    : 0;


            const critical =
                typeof model === "object"
                    ? safeNumber(
                        model.critical
                        ?? model.Critical
                    )
                    : 0;


            const type =
                name === "Phi3 Mini"
                || name === "Qwen 0.5B"
                ? "Local Ollama"
                : "Cloud Model";


            const avatar =
                name.charAt(0)
                    .toUpperCase();


            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "model-card";


            card.innerHTML = `

                <div class="model-header">

                    <div class="model-avatar">
                        ${escapeHTML(avatar)}
                    </div>

                    <div>

                        <strong>
                            ${escapeHTML(name)}
                        </strong>

                        <small>
                            ${escapeHTML(type)}
                        </small>

                    </div>

                </div>


                <div class="model-stats">

                    <div>

                        <span>
                            Average Risk
                        </span>

                        <strong>
                            ${formatNumber(risk, 1)}
                        </strong>

                    </div>


                    <div>

                        <span>
                            Critical
                        </span>

                        <strong>
                            ${formatNumber(critical, 0)}
                        </strong>

                    </div>

                </div>

            `;


            container.appendChild(
                card
            );

        }
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
   CHAT
============================================================ */

function setupChat() {

    const input =
        $("chat-input");

    const button =
        $("send-chat");


    if (!input || !button) {

        return;

    }


    button.addEventListener(
        "click",
        sendChat
    );


    input.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Enter"
            ) {

                event.preventDefault();

                sendChat();

            }

        }
    );

}


async function sendChat() {

    const input =
        $("chat-input");


    const container =
        $("chat-messages");


    if (
        !input ||
        !container
    ) {

        return;

    }


    const message =
        input.value.trim();


    if (!message) {

        return;

    }


    const empty =
        container.querySelector(
            ".chat-empty"
        );


    if (empty) {

        empty.remove();

    }


    appendChatMessage(
        "user",
        message
    );


    input.value =
        "";


    try {

        const response =
            await fetch(
                "/api/chat",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({
                            message
                        })

                }
            );


        if (!response.ok) {

            throw new Error(
                `Chat API returned HTTP ${response.status}`
            );

        }


        const result =
            await response.json();


        const text =
            result.response
            || result.message
            || "No response received.";


        appendChatMessage(
            "assistant",
            text
        );

    }
    catch (error) {

        console.error(
            "[AutoFuzzLLM] Chat error:",
            error
        );


        appendChatMessage(
            "assistant",
            "Backend connection failed. Check the FastAPI terminal."
        );

    }

}


/* ============================================================
   CHAT MESSAGE
============================================================ */

function appendChatMessage(
    role,
    text
) {

    const container =
        $("chat-messages");


    if (!container) {

        return;

    }


    const message =
        document.createElement(
            "div"
        );


    message.style.padding =
        "12px";

    message.style.marginBottom =
        "8px";

    message.style.borderRadius =
        "10px";

    message.style.background =
        role === "user"
            ? "rgba(79,140,255,.10)"
            : "rgba(255,255,255,.04)";


    message.textContent =
        text;


    container.appendChild(
        message
    );


    container.scrollTop =
        container.scrollHeight;

}