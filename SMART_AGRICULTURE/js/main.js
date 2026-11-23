
// ======================================
// SMART AGRICULTURE - MAIN JAVASCRIPT
// ======================================


// ======================================
// 1. COMMON API HELPER
// ======================================

async function apiRequest(url, method = "GET", data = null) {

    const options = {
        method: method,
        credentials: "same-origin",
        cache: "no-store",
        headers: {}
    };

    if (data !== null) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);

    const result = await response.json();

    if (response.status === 401) {
        window.location.href = "/frontend/login.html";
        throw new Error("Please login first.");
    }

    return { response, result };
}


// ======================================
// 2. FARMER LOGIN
// ======================================

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;
        const message = document.getElementById("loginMessage");

        message.textContent = "Please wait...";
        message.style.color = "blue";

        try {

            const { result } = await apiRequest(
                "/api/login",
                "POST",
                { email, password }
            );

            if (result.success) {

                message.textContent = "Login successful!";
                message.style.color = "green";

                window.location.href = "/frontend/dashboard.html";

            } else {

                message.textContent = result.message;
                message.style.color = "red";

            }

        } catch (error) {

            message.textContent =
                error.message || "Server connection failed.";

            message.style.color = "red";

            console.error(error);

        }

    });

}


// ======================================
// 3. FARMER REGISTRATION
// ======================================

const registerForm = document.getElementById("registerForm");

if (registerForm) {

    registerForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const name = document.getElementById("name").value.trim();
        const email = document.getElementById("email").value.trim();
        const phone = document.getElementById("phone").value.trim();

        const password = document.getElementById("password").value;
        const confirmPassword =
            document.getElementById("confirmPassword").value;

        const message = document.getElementById("registerMessage");

        if (password.length < 8) {

            message.textContent =
                "Password must contain at least 8 characters.";

            message.style.color = "red";

            return;

        }

        if (password !== confirmPassword) {

            message.textContent = "Passwords do not match.";
            message.style.color = "red";

            return;

        }

        message.textContent = "Creating account...";
        message.style.color = "blue";

        try {

            const { result } = await apiRequest(
                "/api/register",
                "POST",
                { name, email, phone, password }
            );

            if (result.success) {

                message.textContent =
                    "Registration successful! Redirecting to login...";

                message.style.color = "green";

                setTimeout(() => {
                    window.location.href = "/frontend/login.html";
                }, 1500);

            } else {

                message.textContent = result.message;
                message.style.color = "red";

            }

        } catch (error) {

            message.textContent =
                error.message || "Server connection failed.";

            message.style.color = "red";

            console.error(error);

        }

    });

}


// ======================================
// 4. DASHBOARD SESSION CHECK
// ======================================

async function loadFarmerDashboard() {

    const welcomeMessage =
        document.getElementById("welcomeMessage");

    if (!welcomeMessage) return;

    try {

        const { response, result } =
            await apiRequest("/api/me");

        if (!response.ok || !result.success) {

            window.location.href = "/frontend/login.html";

            return;

        }

        const farmer = result.farmer;

        const farmerId = document.getElementById("farmerId");
        const farmerEmail = document.getElementById("farmerEmail");

        if (farmerId) {
            farmerId.textContent = farmer.farmer_id;
        }

        if (farmerEmail) {
            farmerEmail.textContent = farmer.email;
        }

        const farmerName = farmer.email.split("@")[0];

        welcomeMessage.textContent =
            "Welcome, " + farmerName + "!";

        await loadDashboardStatistics();

    } catch (error) {

        console.error("Dashboard session error:", error);

        const message =
            document.getElementById("dashboardMessage");

        if (message) {
            message.textContent =
                "Unable to load farmer information.";
        }

    }

}


// ======================================
// 5. DASHBOARD STATISTICS
// ======================================

async function loadDashboardStatistics() {

    const statisticsMessage =
        document.getElementById("statisticsMessage");

    if (!document.getElementById("totalFarms")) return;

    try {

        const { response, result } =
            await apiRequest("/api/dashboard-stats");

        if (!response.ok || !result.success) {

            throw new Error(
                result.message || "Unable to load statistics."
            );

        }

        const statistics = result.statistics;

        document.getElementById("totalFarms").textContent =
            statistics.total_farms;

        document.getElementById("totalFields").textContent =
            statistics.total_fields;

        document.getElementById("growingCrops").textContent =
            statistics.growing_crops;

        document.getElementById("totalExpenses").textContent =
            "৳" + Number(statistics.total_expenses).toFixed(2);

        if (statisticsMessage) {
            statisticsMessage.textContent = "";
        }

    } catch (error) {

        console.error("Statistics error:", error);

        if (statisticsMessage) {

            statisticsMessage.textContent =
                "Statistics could not be loaded. Please refresh the page.";

            statisticsMessage.style.color = "red";

        }

    }

}


// ======================================
// 6. FARM MANAGEMENT
// ======================================

const farmForm = document.getElementById("farmForm");
const farmList = document.getElementById("farmList");
const farmMessage = document.getElementById("farmMessage");
const fieldFarm = document.getElementById("fieldFarm");

let farms = [];


function showFarmMessage(message, color = "green") {

    if (!farmMessage) return;

    farmMessage.textContent = message;
    farmMessage.style.color = color;

}


// LOAD FARMS

async function loadFarms() {

    if (!farmList && !fieldFarm) return;

    if (farmList) {
        farmList.innerHTML =
            '<p class="empty-message">Loading farms...</p>';
    }

    try {

        const { response, result } =
            await apiRequest("/api/farms");

        if (!response.ok || !result.success) {

            throw new Error(
                result.message || "Unable to load farms."
            );

        }

        farms = result.farms || [];

        displayFarms();
        updateFarmDropdown();

    } catch (error) {

        console.error("Farm loading error:", error);

        if (farmList) {
            farmList.innerHTML =
                '<p class="empty-message">Unable to load farms.</p>';
        }

    }

}


// DISPLAY FARMS

function displayFarms() {

    if (!farmList) return;

    farmList.innerHTML = "";

    if (farms.length === 0) {

        farmList.innerHTML =
            '<p class="empty-message">No farms found. Add your first farm.</p>';

        return;

    }

    farms.forEach(farm => {

        const card = document.createElement("div");
        card.className = "farm-card";

        const title = document.createElement("h3");
        title.textContent = "🏡 " + farm.farm_name;

        const id = document.createElement("p");
        id.textContent = "Farm ID: " + farm.farm_id;

        const district = document.createElement("p");
        district.textContent = "District: " + farm.district;

        const actions = document.createElement("div");
        actions.className = "card-actions";

        const editButton = document.createElement("button");
        editButton.className = "edit-btn";
        editButton.textContent = "Edit";

        editButton.addEventListener("click", () => {
            editFarm(farm.farm_id);
        });

        const deleteButton = document.createElement("button");
        deleteButton.className = "delete-btn";
        deleteButton.textContent = "Delete";

        deleteButton.addEventListener("click", () => {
            deleteFarm(farm.farm_id);
        });

        actions.append(editButton, deleteButton);

        card.append(title, id, district, actions);

        farmList.appendChild(card);

    });

}


// FARM DROPDOWN

function updateFarmDropdown() {

    if (!fieldFarm) return;

    const selectedValue = fieldFarm.value;

    fieldFarm.innerHTML =
        '<option value="">Select your farm</option>';

    farms.forEach(farm => {

        const option = document.createElement("option");

        option.value = farm.farm_id;

        option.textContent =
            farm.farm_name + " (ID: " + farm.farm_id + ")";

        fieldFarm.appendChild(option);

    });

    if (farms.some(farm => String(farm.farm_id) === selectedValue)) {
        fieldFarm.value = selectedValue;
    }

}


// ADD FARM

if (farmForm) {

    farmForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const farmName =
            document.getElementById("farmName").value.trim();

        const district =
            document.getElementById("farmDistrict").value.trim();

        showFarmMessage("Creating farm...", "blue");

        try {

            const { response, result } = await apiRequest(
                "/api/farms",
                "POST",
                {
                    farm_name: farmName,
                    district: district
                }
            );

            if (!response.ok || !result.success) {

                throw new Error(
                    result.message || "Farm creation failed."
                );

            }

            farmForm.reset();

            showFarmMessage("Farm added successfully!");

            await loadFarms();
            await loadDashboardStatistics();

        } catch (error) {

            showFarmMessage(error.message, "red");

            console.error(error);

        }

    });

}


// EDIT FARM

async function editFarm(farmId) {

    const farm = farms.find(
        item => String(item.farm_id) === String(farmId)
    );

    if (!farm) return;

    const farmName = prompt(
        "Enter new farm name:",
        farm.farm_name
    );

    if (farmName === null) return;

    const district = prompt(
        "Enter new district:",
        farm.district
    );

    if (district === null) return;

    if (!farmName.trim() || !district.trim()) {

        alert("Farm name and district are required.");

        return;

    }

    try {

        const { response, result } = await apiRequest(
            "/api/farms/" + farmId,
            "PUT",
            {
                farm_name: farmName.trim(),
                district: district.trim()
            }
        );

        if (!response.ok || !result.success) {

            throw new Error(
                result.message || "Farm update failed."
            );

        }

        alert("Farm updated successfully!");

        await loadFarms();

    } catch (error) {

        alert(error.message);

    }

}


// DELETE FARM

async function deleteFarm(farmId) {

    const confirmed = confirm(
        "Are you sure you want to delete this farm?"
    );

    if (!confirmed) return;

    try {

        const { response, result } = await apiRequest(
            "/api/farms/" + farmId,
            "DELETE"
        );

        if (!response.ok || !result.success) {

            throw new Error(
                result.message || "Farm deletion failed."
            );

        }

        alert("Farm deleted successfully!");

        await loadFarms();
        await loadFields();
        await loadDashboardStatistics();

    } catch (error) {

        alert(error.message);

    }

}


// REFRESH FARM BUTTON

const refreshFarms =
    document.getElementById("refreshFarms");

if (refreshFarms) {
    refreshFarms.addEventListener("click", loadFarms);
}


// ======================================
// 7. FIELD MANAGEMENT
// ======================================

const fieldForm = document.getElementById("fieldForm");
const fieldList = document.getElementById("fieldList");
const fieldMessage = document.getElementById("fieldMessage");

let fields = [];


function showFieldMessage(message, color = "green") {

    if (!fieldMessage) return;

    fieldMessage.textContent = message;
    fieldMessage.style.color = color;

}


// LOAD FIELDS

async function loadFields() {

    if (!fieldList && !document.getElementById("cycleField")) return;

    if (fieldList) {
        fieldList.innerHTML =
            '<p class="empty-message">Loading fields...</p>';
    }

    try {

        const { response, result } =
            await apiRequest("/api/fields");

        if (!response.ok || !result.success) {

            throw new Error(
                result.message || "Unable to load fields."
            );

        }

        fields = result.fields || [];

        displayFields();
        updatePlantingFieldDropdown();

    } catch (error) {

        console.error("Field loading error:", error);

        if (fieldList) {
            fieldList.innerHTML =
                '<p class="empty-message">Unable to load fields.</p>';
        }

    }

}


// DISPLAY FIELDS

function displayFields() {

    if (!fieldList) return;

    fieldList.innerHTML = "";

    if (fields.length === 0) {

        fieldList.innerHTML =
            '<p class="empty-message">No fields found. Add your first field.</p>';

        return;

    }

    fields.forEach(field => {

        const card = document.createElement("div");
        card.className = "field-card";

        const title = document.createElement("h3");
        title.textContent = "🌱 " + field.field_name;

        const farm = document.createElement("p");
        farm.textContent = "Farm: " + field.farm_name;

        const area = document.createElement("p");
        area.textContent = "Area: " + field.area_acres + " acres";

        const soil = document.createElement("p");
        soil.textContent = "Soil Type: " + field.soil_type;

        const ph = document.createElement("p");
        ph.textContent =
            "Soil pH: " + (field.soil_ph ?? "Not available");

        const actions = document.createElement("div");
        actions.className = "card-actions";

        const editButton = document.createElement("button");
        editButton.className = "edit-btn";
        editButton.textContent = "Edit";

        editButton.addEventListener("click", () => {
            editField(field.field_id);
        });

        const deleteButton = document.createElement("button");
        deleteButton.className = "delete-btn";
        deleteButton.textContent = "Delete";

        deleteButton.addEventListener("click", () => {
            deleteField(field.field_id);
        });

        actions.append(editButton, deleteButton);

        card.append(title, farm, area, soil, ph, actions);

        fieldList.appendChild(card);

    });

}


// ADD FIELD

if (fieldForm) {

    fieldForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const farmId =
            document.getElementById("fieldFarm").value;

        const fieldName =
            document.getElementById("fieldName").value.trim();

        const area =
            document.getElementById("fieldArea").value;

        const soilType =
            document.getElementById("soilType").value;

        const soilPh =
            document.getElementById("soilPh").value;

        if (!farmId) {

            showFieldMessage("Please select a farm.", "red");

            return;

        }

        showFieldMessage("Creating field...", "blue");

        try {

            const { response, result } = await apiRequest(
                "/api/fields",
                "POST",
                {
                    farm_id: Number(farmId),
                    field_name: fieldName,
                    area_acres: Number(area),
                    soil_type: soilType,
                    soil_ph: Number(soilPh)
                }
            );

            if (!response.ok || !result.success) {

                throw new Error(
                    result.message || "Field creation failed."
                );

            }

            fieldForm.reset();

            showFieldMessage("Field added successfully!");

            await loadFields();
            await loadDashboardStatistics();

        } catch (error) {

            showFieldMessage(error.message, "red");

            console.error(error);

        }

    });

}


// EDIT FIELD

async function editField(fieldId) {

    const field = fields.find(
        item => String(item.field_id) === String(fieldId)
    );

    if (!field) return;

    const fieldName = prompt(
        "Enter new field name:",
        field.field_name
    );

    if (fieldName === null) return;

    const area = prompt(
        "Enter field area in acres:",
        field.area_acres
    );

    if (area === null) return;

    const soilType = prompt(
        "Enter soil type:",
        field.soil_type
    );

    if (soilType === null) return;

    const soilPh = prompt(
        "Enter soil pH:",
        field.soil_ph
    );

    if (soilPh === null) return;

    const farmId = prompt(
        "Enter Farm ID:",
        field.farm_id
    );

    if (farmId === null) return;

    if (
        !fieldName.trim() ||
        !soilType.trim() ||
        !Number.isFinite(Number(area)) ||
        Number(area) <= 0 ||
        !Number.isFinite(Number(soilPh)) ||
        Number(soilPh) < 0 ||
        Number(soilPh) > 14 ||
        !Number.isInteger(Number(farmId)) ||
        Number(farmId) <= 0
    ) {

        alert("Please enter valid field information.");

        return;

    }

    try {

        const { response, result } = await apiRequest(
            "/api/fields/" + fieldId,
            "PUT",
            {
                farm_id: Number(farmId),
                field_name: fieldName.trim(),
                area_acres: Number(area),
                soil_type: soilType.trim(),
                soil_ph: Number(soilPh)
            }
        );

        if (!response.ok || !result.success) {

            throw new Error(
                result.message || "Field update failed."
            );

        }

        alert("Field updated successfully!");

        await loadFields();

    } catch (error) {

        alert(error.message);

    }

}


// DELETE FIELD

async function deleteField(fieldId) {

    const confirmed = confirm(
        "Are you sure you want to delete this field?"
    );

    if (!confirmed) return;

    try {

        const { response, result } = await apiRequest(
            "/api/fields/" + fieldId,
            "DELETE"
        );

        if (!response.ok || !result.success) {

            throw new Error(
                result.message || "Field deletion failed."
            );

        }

        alert("Field deleted successfully!");

        await loadFields();
        await loadDashboardStatistics();

    } catch (error) {

        alert(error.message);

    }

}


// REFRESH FIELD BUTTON

const refreshFields =
    document.getElementById("refreshFields");

if (refreshFields) {
    refreshFields.addEventListener("click", loadFields);
}


// ======================================
// 8. FARM & FIELD PAGE INITIALIZATION
// ======================================

async function initializeFarmFieldPage() {

    if (!farmList && !fieldList) return;

    try {

        const { response, result } =
            await apiRequest("/api/me");

        if (!response.ok || !result.success) {

            window.location.href = "/frontend/login.html";

            return;

        }

        const farmerEmail =
            document.getElementById("farmerEmail");

        if (farmerEmail) {
            farmerEmail.textContent = result.farmer.email;
        }

        await loadFarms();
        await loadFields();

    } catch (error) {

        console.error(
            "Farm and field initialization error:",
            error
        );

    }

}


// ======================================
// 9. CROP MANAGEMENT
// ======================================

const cropForm = document.getElementById("cropForm");
const cropList = document.getElementById("cropList");
const cropMessage = document.getElementById("cropMessage");

const cropListMessage =
    document.getElementById("cropListMessage");

let crops = [];


function showCropMessage(message, color = "green") {

    if (!cropMessage) return;

    cropMessage.textContent = message;
    cropMessage.style.color = color;

}


// LOAD CROPS

async function loadCrops() {

    if (!cropList && !document.getElementById("cycleCrop")) return;

    if (cropList) {
        cropList.innerHTML =
            '<p class="empty-message">Loading crops...</p>';
    }

    try {

        const { response, result } =
            await apiRequest("/api/crops");

        if (!response.ok || !result.success) {

            throw new Error(
                result.message || "Unable to load crops."
            );

        }

        crops = result.crops || [];

        displayCrops();
        updatePlantingCropDropdown();

        if (cropListMessage) {

            cropListMessage.textContent =
                crops.length + " crops available.";

        }

    } catch (error) {

        console.error("Crop loading error:", error);

        if (cropList) {
            cropList.innerHTML =
                '<p class="empty-message">Unable to load crops.</p>';
        }

        if (cropListMessage) {
            cropListMessage.textContent = error.message;
        }

    }

}


// DISPLAY CROPS

function displayCrops() {

    if (!cropList) return;

    cropList.innerHTML = "";

    if (crops.length === 0) {

        cropList.innerHTML =
            '<p class="empty-message">No crops available.</p>';

        return;

    }

    crops.forEach(crop => {

        const card = document.createElement("div");
        card.className = "crop-card";

        const title = document.createElement("h3");
        title.textContent = "🌱 " + crop.crop_name;

        const category = document.createElement("p");
        category.textContent =
            "Category: " + (crop.category || "Not specified");

        const duration = document.createElement("p");

        duration.textContent =
            "Growing Duration: " +
            (
                crop.growing_duration_days !== null &&
                crop.growing_duration_days !== undefined
                    ? crop.growing_duration_days + " days"
                    : "Not set"
            );

        const description = document.createElement("p");

        description.textContent =
            crop.description || "No description available.";

        const cropId = document.createElement("small");
        cropId.textContent = "Crop ID: " + crop.crop_id;

        const actions = document.createElement("div");
        actions.className = "card-actions";

        const editButton = document.createElement("button");
        editButton.className = "edit-btn";
        editButton.textContent = "Edit";

        editButton.addEventListener("click", () => {
            editCrop(crop.crop_id);
        });

        const deleteButton = document.createElement("button");
        deleteButton.className = "delete-btn";
        deleteButton.textContent = "Delete";

        deleteButton.addEventListener("click", () => {
            deleteCrop(crop.crop_id);
        });

        actions.append(editButton, deleteButton);

        card.append(
            title,
            category,
            duration,
            description,
            cropId,
            actions
        );

        cropList.appendChild(card);

    });

}


// ADD CROP

if (cropForm) {

    cropForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const cropName =
            document.getElementById("cropName").value.trim();

        const category =
            document.getElementById("cropCategory").value;

        const durationValue =
            document.getElementById("cropDuration").value;

        const description =
            document.getElementById("cropDescription").value.trim();

        const duration = Number(durationValue);

        if (!cropName || !category || !durationValue) {

            showCropMessage(
                "Please fill in all required fields.",
                "red"
            );

            return;

        }

        if (!Number.isInteger(duration) || duration <= 0) {

            showCropMessage(
                "Growing duration must be a positive whole number.",
                "red"
            );

            return;

        }

        showCropMessage("Adding crop...", "blue");

        try {

            const { response, result } = await apiRequest(
                "/api/crops",
                "POST",
                {
                    crop_name: cropName,
                    category: category,
                    growing_duration_days: duration,
                    description: description
                }
            );

            if (!response.ok || !result.success) {

                throw new Error(
                    result.message || "Crop creation failed."
                );

            }

            cropForm.reset();

            showCropMessage("Crop added successfully!");

            await loadCrops();

        } catch (error) {

            showCropMessage(error.message, "red");

            console.error("Crop creation error:", error);

        }

    });

}


// EDIT CROP

async function editCrop(cropId) {

    const crop = crops.find(
        item => String(item.crop_id) === String(cropId)
    );

    if (!crop) return;

    const cropName = prompt(
        "Enter crop name:",
        crop.crop_name
    );

    if (cropName === null) return;

    const category = prompt(
        "Enter category (Cereal, Vegetable, Oilseed, Pulse, Fruit, Other):",
        crop.category || ""
    );

    if (category === null) return;

    const duration = prompt(
        "Enter growing duration in days:",
        crop.growing_duration_days ?? ""
    );

    if (duration === null) return;

    const description = prompt(
        "Enter crop description:",
        crop.description || ""
    );

    if (description === null) return;

    const validCategories = [
        "Cereal",
        "Vegetable",
        "Oilseed",
        "Pulse",
        "Fruit",
        "Other"
    ];

    const normalizedCategory = validCategories.find(
        item => item.toLowerCase() === category.trim().toLowerCase()
    );

    if (
        !cropName.trim() ||
        !normalizedCategory ||
        !Number.isInteger(Number(duration)) ||
        Number(duration) <= 0
    ) {

        alert("Please enter valid crop information.");

        return;

    }

    try {

        const { response, result } = await apiRequest(
            "/api/crops/" + cropId,
            "PUT",
            {
                crop_name: cropName.trim(),
                category: normalizedCategory,
                growing_duration_days: Number(duration),
                description: description.trim()
            }
        );

        if (!response.ok || !result.success) {

            throw new Error(
                result.message || "Crop update failed."
            );

        }

        showCropMessage("Crop updated successfully!");

        await loadCrops();

    } catch (error) {

        showCropMessage(error.message, "red");

        console.error("Crop update error:", error);

        alert(error.message);

    }

}


// DELETE CROP

async function deleteCrop(cropId) {

    const crop = crops.find(
        item => String(item.crop_id) === String(cropId)
    );

    if (!crop) return;

    const confirmed = confirm(
        'Are you sure you want to deactivate "' +
        crop.crop_name +
        '"? It will no longer appear in the active crop list.'
    );

    if (!confirmed) return;

    try {

        const { response, result } = await apiRequest(
            "/api/crops/" + cropId,
            "DELETE"
        );

        if (!response.ok || !result.success) {

            throw new Error(
                result.message || "Crop deletion failed."
            );

        }

        showCropMessage("Crop deactivated successfully!");

        await loadCrops();

    } catch (error) {

        showCropMessage(error.message, "red");

        console.error("Crop deletion error:", error);

        alert(error.message);

    }

}


// REFRESH CROP BUTTON

const refreshCrops =
    document.getElementById("refreshCrops");

if (refreshCrops) {
    refreshCrops.addEventListener("click", loadCrops);
}


// CROP PAGE INITIALIZATION

async function initializeCropPage() {

    if (!cropList) return;

    try {

        const { response, result } =
            await apiRequest("/api/me");

        if (!response.ok || !result.success) {

            window.location.href = "/frontend/login.html";

            return;

        }

        const farmerEmail =
            document.getElementById("farmerEmail");

        if (farmerEmail) {
            farmerEmail.textContent = result.farmer.email;
        }

        await loadCrops();

    } catch (error) {

        console.error(
            "Crop page initialization error:",
            error
        );

    }

}


// ======================================
// 10. PLANTING CYCLE MANAGEMENT
// ======================================

const plantingForm = document.getElementById("plantingForm");

const plantingCycleList =
    document.getElementById("plantingCycleList");

const plantingMessage =
    document.getElementById("plantingMessage");

const cycleListMessage =
    document.getElementById("cycleListMessage");

const cycleField =
    document.getElementById("cycleField");

const cycleCrop =
    document.getElementById("cycleCrop");

const cycleIdInput =
    document.getElementById("cycleId");

const plantingDateInput =
    document.getElementById("plantingDate");

const harvestDateInput =
    document.getElementById("harvestDate");

const cycleStatus =
    document.getElementById("cycleStatus");

const statusGroup =
    document.getElementById("statusGroup");

const plantingFormTitle =
    document.getElementById("plantingFormTitle");

const saveCycleBtn =
    document.getElementById("saveCycleBtn");

const cancelEditBtn =
    document.getElementById("cancelEditBtn");

let plantingCycles = [];


// SHOW MESSAGE

function showPlantingMessage(message, color = "green") {

    if (!plantingMessage) return;

    plantingMessage.textContent = message;
    plantingMessage.style.color = color;

}


// FIELD DROPDOWN

function updatePlantingFieldDropdown() {

    if (!cycleField) return;

    const selectedValue = cycleField.value;

    cycleField.innerHTML =
        '<option value="">Select your field</option>';

    fields.forEach(field => {

        const option = document.createElement("option");

        option.value = field.field_id;

        option.textContent =
            field.field_name +
            " - " +
            field.farm_name +
            " (" +
            field.area_acres +
            " acres)";

        cycleField.appendChild(option);

    });

    if (fields.some(field => String(field.field_id) === selectedValue)) {
        cycleField.value = selectedValue;
    }

    if (fields.length === 0) {

        cycleField.innerHTML =
            '<option value="">No fields available. Add a field first.</option>';

    }

}


// CROP DROPDOWN

function updatePlantingCropDropdown() {

    if (!cycleCrop) return;

    const selectedValue = cycleCrop.value;

    cycleCrop.innerHTML =
        '<option value="">Select a crop</option>';

    crops.forEach(crop => {

        const option = document.createElement("option");

        option.value = crop.crop_id;

        option.textContent =
            crop.crop_name +
            (
                crop.growing_duration_days
                    ? " (" + crop.growing_duration_days + " days)"
                    : ""
            );

        cycleCrop.appendChild(option);

    });

    if (crops.some(crop => String(crop.crop_id) === selectedValue)) {
        cycleCrop.value = selectedValue;
    }

    if (crops.length === 0) {

        cycleCrop.innerHTML =
            '<option value="">No active crops available. Add a crop first.</option>';

    }

}


// LOAD PLANTING CYCLES

async function loadPlantingCycles() {

    if (!plantingCycleList) return;

    plantingCycleList.innerHTML =
        '<p class="empty-message">Loading planting cycles...</p>';

    if (cycleListMessage) {
        cycleListMessage.textContent = "";
    }

    try {

        const { response, result } =
            await apiRequest("/api/planting-cycles");

        if (!response.ok || !result.success) {

            throw new Error(
                result.message || "Unable to load planting cycles."
            );

        }

        plantingCycles = result.planting_cycles || [];

        displayPlantingCycles();

    } catch (error) {

        console.error("Planting cycle loading error:", error);

        plantingCycleList.innerHTML = "";

        if (cycleListMessage) {
            cycleListMessage.textContent = error.message;
        }

    }

}


// DISPLAY PLANTING CYCLES

function displayPlantingCycles() {

    if (!plantingCycleList) return;

    plantingCycleList.innerHTML = "";

    if (plantingCycles.length === 0) {

        if (cycleListMessage) {
            cycleListMessage.textContent =
                "No planting cycles found. Add your first planting cycle.";
        }

        return;

    }

    if (cycleListMessage) {
        cycleListMessage.textContent =
            plantingCycles.length + " planting cycle(s) found.";
    }

    plantingCycles.forEach(cycle => {

        const card = document.createElement("div");
        card.className = "cycle-card";

        const title = document.createElement("h3");
        title.textContent = "🌱 " + cycle.crop_name;

        const farm = document.createElement("p");
        farm.textContent = "Farm: " + cycle.farm_name;

        const field = document.createElement("p");
        field.textContent = "Field: " + cycle.field_name;

        const plantingDate = document.createElement("p");
        plantingDate.textContent =
            "Planting Date: " + cycle.planting_date;

        const harvestDate = document.createElement("p");
        harvestDate.textContent =
            "Expected Harvest: " + cycle.expected_harvest_date;

        const status = document.createElement("span");
        status.className = "cycle-status";
        status.textContent = cycle.status;

        const actions = document.createElement("div");
        actions.className = "cycle-actions";

        const editButton = document.createElement("button");
        editButton.className = "edit-btn";
        editButton.textContent = "Edit";

        editButton.addEventListener("click", function () {
            editPlantingCycle(cycle.cycle_id);
        });

        const deleteButton = document.createElement("button");
        deleteButton.className = "delete-btn";
        deleteButton.textContent = "Delete";

        deleteButton.addEventListener("click", function () {
            deletePlantingCycle(cycle.cycle_id);
        });

        actions.append(editButton, deleteButton);

        card.append(
            title,
            farm,
            field,
            plantingDate,
            harvestDate,
            status,
            actions
        );

        plantingCycleList.appendChild(card);

    });

}


// RESET FORM

function resetPlantingForm() {

    if (!plantingForm) return;

    plantingForm.reset();

    if (cycleIdInput) {
        cycleIdInput.value = "";
    }

    if (plantingFormTitle) {
        plantingFormTitle.textContent = "Add New Planting Cycle";
    }

    if (saveCycleBtn) {
        saveCycleBtn.textContent = "Save Planting Cycle";
    }

    if (statusGroup) {
        statusGroup.hidden = true;
    }

    if (cancelEditBtn) {
        cancelEditBtn.hidden = true;
    }

    showPlantingMessage("");

}


// ADD / UPDATE PLANTING CYCLE

if (plantingForm) {

    plantingForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const fieldId = Number(cycleField.value);
        const cropId = Number(cycleCrop.value);

        const plantingDate = plantingDateInput.value;
        const harvestDate = harvestDateInput.value;

        const cycleId = cycleIdInput.value;

        if (!fieldId || !cropId) {

            showPlantingMessage(
                "Please select a field and crop.",
                "red"
            );

            return;

        }

        if (!plantingDate || !harvestDate) {

            showPlantingMessage(
                "Please select both dates.",
                "red"
            );

            return;

        }

        if (harvestDate < plantingDate) {

            showPlantingMessage(
                "Expected harvest date cannot be earlier than planting date.",
                "red"
            );

            return;

        }

        const data = {
            field_id: fieldId,
            crop_id: cropId,
            planting_date: plantingDate,
            expected_harvest_date: harvestDate
        };

        const isEditing = Boolean(cycleId);

        if (isEditing) {
            data.status = cycleStatus.value;
        }

        showPlantingMessage(
            isEditing
                ? "Updating planting cycle..."
                : "Creating planting cycle...",
            "blue"
        );

        try {

            const url = isEditing
                ? "/api/planting-cycles/" + cycleId
                : "/api/planting-cycles";

            const method = isEditing ? "PUT" : "POST";

            const { response, result } = await apiRequest(
                url,
                method,
                data
            );

            if (!response.ok || !result.success) {

                throw new Error(
                    result.message || "Planting cycle operation failed."
                );

            }

            resetPlantingForm();

            showPlantingMessage(
                isEditing
                    ? "Planting cycle updated successfully!"
                    : "Planting cycle created successfully!"
            );

            await loadPlantingCycles();
            await loadDashboardStatistics();

        } catch (error) {

            showPlantingMessage(error.message, "red");

            console.error("Planting cycle save error:", error);

        }

    });

}


// EDIT PLANTING CYCLE

async function editPlantingCycle(cycleId) {

    const cycle = plantingCycles.find(
        item => String(item.cycle_id) === String(cycleId)
    );

    if (!cycle) return;

    if (fields.length === 0) {
        await loadFields();
    }

    if (crops.length === 0) {
        await loadCrops();
    }

    cycleIdInput.value = cycle.cycle_id;

    cycleField.value = cycle.field_id;
    cycleCrop.value = cycle.crop_id;

    plantingDateInput.value = cycle.planting_date;
    harvestDateInput.value = cycle.expected_harvest_date;

    if (cycleStatus) {
        cycleStatus.value = cycle.status;
    }

    if (statusGroup) {
        statusGroup.hidden = false;
    }

    if (plantingFormTitle) {
        plantingFormTitle.textContent = "Edit Planting Cycle";
    }

    if (saveCycleBtn) {
        saveCycleBtn.textContent = "Update Planting Cycle";
    }

    if (cancelEditBtn) {
        cancelEditBtn.hidden = false;
    }

    showPlantingMessage(
        "Editing cycle #" + cycle.cycle_id,
        "blue"
    );

    plantingForm.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

}


// CANCEL EDIT

if (cancelEditBtn) {

    cancelEditBtn.addEventListener("click", function () {

        resetPlantingForm();

    });

}


// DELETE PLANTING CYCLE

async function deletePlantingCycle(cycleId) {

    const cycle = plantingCycles.find(
        item => String(item.cycle_id) === String(cycleId)
    );

    if (!cycle) return;

    const confirmed = confirm(
        'Are you sure you want to delete the "' +
        cycle.crop_name +
        '" planting cycle?'
    );

    if (!confirmed) return;

    try {

        const { response, result } = await apiRequest(
            "/api/planting-cycles/" + cycleId,
            "DELETE"
        );

        if (!response.ok || !result.success) {

            throw new Error(
                result.message || "Planting cycle deletion failed."
            );

        }

        alert("Planting cycle deleted successfully!");

        resetPlantingForm();

        await loadPlantingCycles();
        await loadDashboardStatistics();

    } catch (error) {

        console.error("Planting cycle deletion error:", error);

        alert(error.message);

    }

}


// INITIALIZE PLANTING PAGE

async function initializePlantingPage() {

    if (!plantingForm) return;

    try {

        const { response, result } =
            await apiRequest("/api/me");

        if (!response.ok || !result.success) {

            window.location.href = "/frontend/login.html";

            return;

        }

        const farmerEmail =
            document.getElementById("farmerEmail");

        if (farmerEmail) {
            farmerEmail.textContent = result.farmer.email;
        }

        await loadFields();
        await loadCrops();
        await loadPlantingCycles();

    } catch (error) {

        console.error("Planting page initialization error:", error);

        showPlantingMessage(
            "Unable to initialize planting page: " + error.message,
            "red"
        );

    }

}


// ======================================
// 11. FARMER LOGOUT
// ======================================

const logoutBtn = document.getElementById("logoutBtn");

if (logoutBtn) {

    logoutBtn.addEventListener("click", async function () {

        try {

            const { result } = await apiRequest(
                "/api/logout",
                "POST"
            );

            if (result.success) {

                window.location.href = "/frontend/login.html";

            } else {

                alert(result.message || "Logout failed.");

            }

        } catch (error) {

            console.error("Logout error:", error);

            alert("Unable to logout. Please try again.");

        }

    });

}


// ======================================
// 12. INITIALIZE APPLICATION
// ======================================

loadFarmerDashboard();

initializeFarmFieldPage();

initializeCropPage();

initializePlantingPage();


// ======================================
// FARMING ACTIVITIES MANAGEMENT
// Add this section at the END of main.js
// ======================================

let farmingActivities = [];
let activityPlantingCycles = [];


// HTML SAFE TEXT

function escapeActivityHTML(value) {

    return String(value ?? "").replace(/[&<>"']/g, function(char) {

        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        };

        return entities[char];

    });
}


// SHOW ACTIVITY MESSAGE

function showActivityMessage(message, type = "success") {

    const box = document.getElementById("activityMessage");

    if (!box) return;

    box.textContent = message;
    box.className = "activity-message " + type;

}


// SHOW LIST MESSAGE

function showActivityListMessage(message, type = "error") {

    const box = document.getElementById("activityListMessage");

    if (!box) return;

    box.textContent = message;
    box.className = "activity-message " + type;

}


// ACTIVITY API REQUEST

async function activityAPI(url, method = "GET", data = null) {

    const options = {
        method: method,
        credentials: "same-origin",
        headers: {}
    };

    if (data !== null) {

        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(data);

    }

    const response = await fetch(url, options);

    let result;

    try {
        result = await response.json();
    } catch {
        throw new Error("Invalid server response.");
    }

    if (!response.ok || !result.success) {

        throw new Error(
            result.message || "Something went wrong."
        );

    }

    return result;

}


// LOAD LOGGED-IN FARMER

async function loadActivityFarmer() {

    const emailElement = document.getElementById("farmerEmail");

    if (!emailElement) return;

    try {

        const result = await activityAPI("/api/me");

        emailElement.textContent =
            result.farmer.email || "Farmer";

    } catch (error) {

        window.location.href = "/frontend/login.html";

    }

}


// LOAD PLANTING CYCLES

async function loadActivityPlantingCycles() {

    const dropdown = document.getElementById("activityCycle");

    if (!dropdown) return;

    try {

        const result = await activityAPI("/api/planting-cycles");

        activityPlantingCycles = result.planting_cycles || [];

        dropdown.innerHTML =
            '<option value="">Select planting cycle</option>';

        activityPlantingCycles.forEach(cycle => {

            const option = document.createElement("option");

            option.value = cycle.cycle_id;

            option.textContent =
                `${cycle.crop_name} - ${cycle.field_name} (${cycle.farm_name})`;

            dropdown.appendChild(option);

        });

        if (activityPlantingCycles.length === 0) {

            dropdown.innerHTML =
                '<option value="">No planting cycle available - create one first</option>';

        }

    } catch (error) {

        console.error("Planting cycle loading error:", error);

        dropdown.innerHTML =
            '<option value="">Unable to load planting cycles</option>';

    }

}


// LOAD ACTIVITIES

async function loadFarmingActivities() {

    const tableBody = document.getElementById("activityTableBody");

    if (!tableBody) return;

    tableBody.innerHTML = `
        <tr>
            <td colspan="6" class="activity-empty">
                Loading activities...
            </td>
        </tr>
    `;

    try {

        const result = await activityAPI("/api/activities");

        farmingActivities = result.activities || [];

        renderFarmingActivities();

        showActivityListMessage("", "success");

    } catch (error) {

        console.error("Activity loading error:", error);

        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="activity-empty">
                    Unable to load activities.
                </td>
            </tr>
        `;

        showActivityListMessage(error.message, "error");

    }

}


// DISPLAY ACTIVITIES

function renderFarmingActivities() {

    const tableBody = document.getElementById("activityTableBody");

    if (!tableBody) return;

    if (farmingActivities.length === 0) {

        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="activity-empty">
                    No farming activities found. Add your first activity.
                </td>
            </tr>
        `;

    } else {

        tableBody.innerHTML = farmingActivities.map(activity => {

            return `
                <tr>

                    <td>
                        <span class="activity-type-badge">
                            ${escapeActivityHTML(activity.activity_type)}
                        </span>
                    </td>

                    <td>
                        ${escapeActivityHTML(activity.crop_name)}
                    </td>

                    <td>
                        ${escapeActivityHTML(activity.field_name)}
                    </td>

                    <td>
                        ${escapeActivityHTML(activity.activity_date)}
                    </td>

                    <td>
                        ৳${Number(activity.cost || 0).toFixed(2)}
                    </td>

                    <td>

                        <button
                            type="button"
                            class="activity-btn activity-btn-edit"
                            data-activity-edit="${activity.activity_id}"
                        >
                            Edit
                        </button>

                        <button
                            type="button"
                            class="activity-btn activity-btn-delete"
                            data-activity-delete="${activity.activity_id}"
                        >
                            Delete
                        </button>

                    </td>

                </tr>
            `;

        }).join("");

    }

    updateActivitySummary();

}


// UPDATE SUMMARY CARDS

function updateActivitySummary() {

    const totalElement = document.getElementById("totalActivities");
    const costElement = document.getElementById("totalActivityCost");
    const typesElement = document.getElementById("activityTypeCount");

    if (!totalElement || !costElement || !typesElement) return;

    const totalCost = farmingActivities.reduce(
        (sum, activity) => sum + Number(activity.cost || 0),
        0
    );

    const uniqueTypes = new Set(
        farmingActivities.map(activity => activity.activity_type)
    );

    totalElement.textContent = farmingActivities.length;

    costElement.textContent =
        "৳" + totalCost.toFixed(2);

    typesElement.textContent = uniqueTypes.size;

}


// RESET ACTIVITY FORM

function resetActivityForm() {

    const form = document.getElementById("activityForm");

    if (!form) return;

    form.reset();

    document.getElementById("activityId").value = "";

    document.getElementById("activityFormTitle").textContent =
        "Add New Activity";

    document.getElementById("saveActivityBtn").textContent =
        "Save Activity";

    document.getElementById("cancelActivityEditBtn").style.display =
        "none";

    document.getElementById("activityCost").value = "0";

    const dateInput = document.getElementById("activityDate");

    // Set today's local date

    const today = new Date();

    const localDate =
        today.getFullYear() + "-" +
        String(today.getMonth() + 1).padStart(2, "0") + "-" +
        String(today.getDate()).padStart(2, "0");

    dateInput.value = localDate;

}


// EDIT ACTIVITY

function editFarmingActivity(activityId) {

    const activity = farmingActivities.find(
        item => Number(item.activity_id) === Number(activityId)
    );

    if (!activity) {

        alert("Activity not found.");

        return;

    }

    document.getElementById("activityId").value =
        activity.activity_id;

    document.getElementById("activityCycle").value =
        activity.cycle_id;

    document.getElementById("activityType").value =
        activity.activity_type;

    document.getElementById("activityDate").value =
        activity.activity_date;

    document.getElementById("activityCost").value =
        activity.cost;

    document.getElementById("activityDescription").value =
        activity.description || "";

    document.getElementById("activityFormTitle").textContent =
        "Edit Farming Activity";

    document.getElementById("saveActivityBtn").textContent =
        "Update Activity";

    document.getElementById("cancelActivityEditBtn").style.display =
        "inline-block";

    document.getElementById("activityMessage").className =
        "activity-message";

    document.getElementById("activityForm").scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

}


// DELETE ACTIVITY

async function deleteFarmingActivity(activityId) {

    const confirmed = confirm(
        "Are you sure you want to delete this farming activity?"
    );

    if (!confirmed) return;

    try {

        const result = await activityAPI(
            `/api/activities/${activityId}`,
            "DELETE"
        );

        showActivityListMessage(
            result.message,
            "success"
        );

        await loadFarmingActivities();

        if (
            Number(document.getElementById("activityId").value) ===
            Number(activityId)
        ) {

            resetActivityForm();

        }

    } catch (error) {

        showActivityListMessage(
            error.message,
            "error"
        );

    }

}


// SAVE / UPDATE ACTIVITY

async function submitFarmingActivity(event) {

    event.preventDefault();

    const activityId =
        document.getElementById("activityId").value;

    const data = {

        cycle_id: document.getElementById("activityCycle").value,

        activity_type: document.getElementById("activityType").value,

        activity_date: document.getElementById("activityDate").value,

        cost: document.getElementById("activityCost").value || 0,

        description:
            document.getElementById("activityDescription").value.trim()

    };

    if (!data.cycle_id) {

        showActivityMessage(
            "Please select a planting cycle.",
            "error"
        );

        return;

    }

    if (!data.activity_type) {

        showActivityMessage(
            "Please select an activity type.",
            "error"
        );

        return;

    }

    if (!data.activity_date) {

        showActivityMessage(
            "Please select an activity date.",
            "error"
        );

        return;

    }

    if (Number(data.cost) < 0 || !Number.isFinite(Number(data.cost))) {

        showActivityMessage(
            "Please enter a valid non-negative cost.",
            "error"
        );

        return;

    }

    const saveButton = document.getElementById("saveActivityBtn");

    saveButton.disabled = true;

    saveButton.textContent = activityId
        ? "Updating..."
        : "Saving...";

    try {

        let result;

        if (activityId) {

            result = await activityAPI(
                `/api/activities/${activityId}`,
                "PUT",
                data
            );

        } else {

            result = await activityAPI(
                "/api/activities",
                "POST",
                data
            );

        }

        showActivityMessage(
            result.message,
            "success"
        );

        resetActivityForm();

        await loadFarmingActivities();

    } catch (error) {

        showActivityMessage(
            error.message,
            "error"
        );

    } finally {

        saveButton.disabled = false;

        saveButton.textContent =
            document.getElementById("activityId").value
                ? "Update Activity"
                : "Save Activity";

    }

}


// INITIALIZE ACTIVITIES PAGE

async function initializeActivitiesPage() {

    const activityForm = document.getElementById("activityForm");

    if (!activityForm) return;

    await loadActivityFarmer();

    await loadActivityPlantingCycles();

    resetActivityForm();

    await loadFarmingActivities();

    activityForm.addEventListener(
        "submit",
        submitFarmingActivity
    );

    document.getElementById("cancelActivityEditBtn")
        .addEventListener("click", function() {

            resetActivityForm();

            document.getElementById("activityMessage").className =
                "activity-message";

        });

    // Event delegation for Edit and Delete

    document.getElementById("activityTableBody")
        .addEventListener("click", function(event) {

            const editButton = event.target.closest(
                "[data-activity-edit]"
            );

            const deleteButton = event.target.closest(
                "[data-activity-delete]"
            );

            if (editButton) {

                editFarmingActivity(
                    editButton.dataset.activityEdit
                );

            }

            if (deleteButton) {

                deleteFarmingActivity(
                    deleteButton.dataset.activityDelete
                );

            }

        });

}


// RUN ACTIVITIES INITIALIZATION

initializeActivitiesPage();


// ======================================
// 13. EXPENSE MANAGEMENT
// ======================================

let expenses = [];
let expensePlantingCycles = [];


// ======================================
// 1. EXPENSE API HELPER
// ======================================

async function expenseAPI(url, method = "GET", data = null) {

    const options = {
        method: method,
        credentials: "same-origin",
        cache: "no-store",
        headers: {}
    };

    if (data !== null) {

        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(data);

    }

    const response = await fetch(url, options);

    let result;

    try {
        result = await response.json();
    } catch {
        throw new Error("Invalid server response.");
    }

    if (response.status === 401) {

        window.location.href = "/frontend/login.html";

        throw new Error("Please login first.");

    }

    if (!response.ok || !result.success) {

        throw new Error(
            result.message || "Something went wrong."
        );

    }

    return result;

}


// ======================================
// 2. EXPENSE MESSAGE
// ======================================

function showExpenseMessage(message, type = "success") {

    const box = document.getElementById("expenseMessage");

    if (!box) return;

    box.textContent = message;

    box.className = "expense-message " + type;

}


// ======================================
// 3. EXPENSE LIST MESSAGE
// ======================================

function showExpenseListMessage(message, type = "error") {

    const box = document.getElementById("expenseListMessage");

    if (!box) return;

    box.textContent = message;

    box.className = "expense-message " + type;

}


// ======================================
// 4. LOAD FARMER INFORMATION
// ======================================

async function loadExpenseFarmer() {

    const emailElement = document.getElementById("farmerEmail");

    if (!emailElement) return;

    try {

        const result = await expenseAPI("/api/me");

        emailElement.textContent =
            result.farmer.email || "Farmer";

    } catch (error) {

        console.error("Expense farmer loading error:", error);

        window.location.href = "/frontend/login.html";

    }

}


// ======================================
// 5. LOAD PLANTING CYCLE DROPDOWN
// ======================================

async function loadExpensePlantingCycles() {

    const dropdown = document.getElementById("expenseCycle");

    if (!dropdown) return;

    dropdown.innerHTML =
        '<option value="">Loading planting cycles...</option>';

    try {

        const result = await expenseAPI("/api/planting-cycles");

        expensePlantingCycles = result.planting_cycles || [];

        dropdown.innerHTML =
            '<option value="">Select planting cycle</option>';

        expensePlantingCycles.forEach(cycle => {

            const option = document.createElement("option");

            option.value = cycle.cycle_id;

            option.textContent =
                `${cycle.crop_name} - ${cycle.field_name} (${cycle.farm_name})`;

            dropdown.appendChild(option);

        });

        if (expensePlantingCycles.length === 0) {

            dropdown.innerHTML =
                '<option value="">No planting cycles available - create one first</option>';

        }

    } catch (error) {

        console.error("Expense cycle loading error:", error);

        dropdown.innerHTML =
            '<option value="">Unable to load planting cycles</option>';

    }

}


// ======================================
// 6. LOAD EXPENSES
// ======================================

async function loadExpenses() {

    const tableBody = document.getElementById("expenseTableBody");

    if (!tableBody) return;

    tableBody.innerHTML = `
        <tr>
            <td colspan="6" class="expense-empty">
                Loading expenses...
            </td>
        </tr>
    `;

    try {

        const result = await expenseAPI("/api/expenses");

        expenses = result.expenses || [];

        renderExpenses();

        showExpenseListMessage("", "success");

    } catch (error) {

        console.error("Expense loading error:", error);

        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="expense-empty">
                    Unable to load expenses.
                </td>
            </tr>
        `;

        showExpenseListMessage(error.message, "error");

    }

}


// ======================================
// 7. SAFE HTML TEXT
// ======================================

function escapeExpenseHTML(value) {

    return String(value ?? "").replace(/[&<>"']/g, function(char) {

        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        };

        return entities[char];

    });

}


// ======================================
// 8. DISPLAY EXPENSES
// ======================================

function renderExpenses() {

    const tableBody = document.getElementById("expenseTableBody");

    if (!tableBody) return;

    if (expenses.length === 0) {

        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="expense-empty">
                    No expenses found. Add your first expense.
                </td>
            </tr>
        `;

    } else {

        tableBody.innerHTML = expenses.map(expense => {

            return `
                <tr>

                    <td>
                        <span class="expense-type-badge">
                            ${escapeExpenseHTML(expense.expense_type)}
                        </span>

                        ${
                            expense.description
                                ? `<small title="${escapeExpenseHTML(expense.description)}">
                                    ${escapeExpenseHTML(expense.description)}
                                   </small>`
                                : ""
                        }
                    </td>

                    <td>
                        ${escapeExpenseHTML(expense.crop_name)}
                    </td>

                    <td>
                        ${escapeExpenseHTML(expense.field_name)}
                    </td>

                    <td>
                        ${escapeExpenseHTML(expense.expense_date)}
                    </td>

                    <td>
                        ৳${Number(expense.amount || 0).toFixed(2)}
                    </td>

                    <td>

                        <button
                            type="button"
                            class="expense-btn expense-btn-edit"
                            data-expense-edit="${Number(expense.expense_id)}"
                        >
                            Edit
                        </button>

                        <button
                            type="button"
                            class="expense-btn expense-btn-delete"
                            data-expense-delete="${Number(expense.expense_id)}"
                        >
                            Delete
                        </button>

                    </td>

                </tr>
            `;

        }).join("");

    }

    updateExpenseSummary();

}


// ======================================
// 9. UPDATE EXPENSE SUMMARY
// ======================================

function updateExpenseSummary() {

    const totalElement =
        document.getElementById("totalExpenseAmount");

    const countElement =
        document.getElementById("expenseCount");

    const monthlyElement =
        document.getElementById("monthlyExpenseAmount");

    if (!totalElement || !countElement || !monthlyElement) return;

    const totalAmount = expenses.reduce(
        (sum, expense) => sum + Number(expense.amount || 0),
        0
    );

    const today = new Date();

    const currentYear = today.getFullYear();

    const currentMonth = today.getMonth() + 1;

    const monthlyAmount = expenses.reduce(
        (sum, expense) => {

            if (!expense.expense_date) return sum;

            const parts = expense.expense_date.split("-");

            const year = Number(parts[0]);
            const month = Number(parts[1]);

            if (year === currentYear && month === currentMonth) {

                return sum + Number(expense.amount || 0);

            }

            return sum;

        },
        0
    );

    totalElement.textContent =
        "৳" + totalAmount.toFixed(2);

    countElement.textContent = expenses.length;

    monthlyElement.textContent =
        "৳" + monthlyAmount.toFixed(2);

}


// ======================================
// 10. RESET EXPENSE FORM
// ======================================

function resetExpenseForm() {

    const form = document.getElementById("expenseForm");

    if (!form) return;

    form.reset();

    document.getElementById("expenseId").value = "";

    document.getElementById("expenseFormTitle").textContent =
        "Add New Expense";

    document.getElementById("saveExpenseBtn").textContent =
        "Save Expense";

    const cancelButton =
        document.getElementById("cancelExpenseEditBtn");

    if (cancelButton) {
        cancelButton.hidden = true;
    }

    const dateInput =
        document.getElementById("expenseDate");

    if (dateInput) {

        const today = new Date();

        const localDate =
            today.getFullYear() + "-" +
            String(today.getMonth() + 1).padStart(2, "0") + "-" +
            String(today.getDate()).padStart(2, "0");

        dateInput.value = localDate;

    }

    showExpenseMessage("", "success");

}


// ======================================
// 11. EDIT EXPENSE
// ======================================

function editExpense(expenseId) {

    const expense = expenses.find(
        item => Number(item.expense_id) === Number(expenseId)
    );

    if (!expense) {

        alert("Expense not found.");

        return;

    }

    document.getElementById("expenseId").value =
        expense.expense_id;

    document.getElementById("expenseCycle").value =
        expense.cycle_id;

    document.getElementById("expenseType").value =
        expense.expense_type;

    document.getElementById("expenseDate").value =
        expense.expense_date;

    document.getElementById("expenseAmount").value =
        expense.amount;

    document.getElementById("expenseDescription").value =
        expense.description || "";

    document.getElementById("expenseFormTitle").textContent =
        "Edit Expense";

    document.getElementById("saveExpenseBtn").textContent =
        "Update Expense";

    const cancelButton =
        document.getElementById("cancelExpenseEditBtn");

    if (cancelButton) {
        cancelButton.hidden = false;
    }

    showExpenseMessage(
        "Editing expense #" + expense.expense_id,
        "success"
    );

    document.getElementById("expenseForm").scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

}


// ======================================
// 12. DELETE EXPENSE
// ======================================

async function deleteExpense(expenseId) {

    const expense = expenses.find(
        item => Number(item.expense_id) === Number(expenseId)
    );

    if (!expense) return;

    const confirmed = confirm(
        "Are you sure you want to delete this expense?"
    );

    if (!confirmed) return;

    try {

        const result = await expenseAPI(
            `/api/expenses/${expenseId}`,
            "DELETE"
        );

        showExpenseListMessage(
            result.message || "Expense deleted successfully!",
            "success"
        );

        if (
            Number(document.getElementById("expenseId").value) ===
            Number(expenseId)
        ) {

            resetExpenseForm();

        }

        await loadExpenses();

        await loadDashboardStatistics();

    } catch (error) {

        console.error("Expense deletion error:", error);

        showExpenseListMessage(
            error.message,
            "error"
        );

    }

}


// ======================================
// 13. ADD / UPDATE EXPENSE
// ======================================

async function submitExpense(event) {

    event.preventDefault();

    const expenseId =
        document.getElementById("expenseId").value;

    const data = {

        cycle_id:
            document.getElementById("expenseCycle").value,

        expense_type:
            document.getElementById("expenseType").value,

        expense_date:
            document.getElementById("expenseDate").value,

        amount:
            document.getElementById("expenseAmount").value,

        description:
            document.getElementById("expenseDescription").value.trim()

    };


    // VALIDATION

    if (!data.cycle_id) {

        showExpenseMessage(
            "Please select a planting cycle.",
            "error"
        );

        return;

    }

    if (!data.expense_type) {

        showExpenseMessage(
            "Please select an expense category.",
            "error"
        );

        return;

    }

    if (!data.expense_date) {

        showExpenseMessage(
            "Please select an expense date.",
            "error"
        );

        return;

    }

    if (
        data.amount === "" ||
        !Number.isFinite(Number(data.amount)) ||
        Number(data.amount) <= 0 ||
        Number(data.amount) > 99999999.99
    ) {

        showExpenseMessage(
            "Please enter a valid expense amount.",
            "error"
        );

        return;

    }


    const saveButton =
        document.getElementById("saveExpenseBtn");

    saveButton.disabled = true;

    saveButton.textContent = expenseId
        ? "Updating..."
        : "Saving...";


    try {

        let result;

        if (expenseId) {

            result = await expenseAPI(
                `/api/expenses/${expenseId}`,
                "PUT",
                data
            );

        } else {

            result = await expenseAPI(
                "/api/expenses",
                "POST",
                data
            );

        }

        showExpenseMessage(
            result.message || "Expense saved successfully!",
            "success"
        );

        resetExpenseForm();

        await loadExpenses();

        await loadDashboardStatistics();

    } catch (error) {

        console.error("Expense save error:", error);

        showExpenseMessage(
            error.message,
            "error"
        );

    } finally {

        saveButton.disabled = false;

        saveButton.textContent =
            document.getElementById("expenseId").value
                ? "Update Expense"
                : "Save Expense";

    }

}


// ======================================
// 14. INITIALIZE EXPENSES PAGE
// ======================================

async function initializeExpensesPage() {

    const expenseForm =
        document.getElementById("expenseForm");

    if (!expenseForm) return;

    try {

        await loadExpenseFarmer();

        await loadExpensePlantingCycles();

        resetExpenseForm();

        await loadExpenses();


        // FORM SUBMIT

        expenseForm.addEventListener(
            "submit",
            submitExpense
        );


        // CANCEL EDIT

        const cancelButton =
            document.getElementById("cancelExpenseEditBtn");

        if (cancelButton) {

            cancelButton.addEventListener("click", function() {

                resetExpenseForm();

            });

        }


        // TABLE EDIT AND DELETE

        const tableBody =
            document.getElementById("expenseTableBody");

        if (tableBody) {

            tableBody.addEventListener("click", function(event) {

                const editButton = event.target.closest(
                    "[data-expense-edit]"
                );

                const deleteButton = event.target.closest(
                    "[data-expense-delete]"
                );

                if (editButton) {

                    editExpense(
                        editButton.dataset.expenseEdit
                    );

                }

                if (deleteButton) {

                    deleteExpense(
                        deleteButton.dataset.expenseDelete
                    );

                }

            });

        }


        // REFRESH EXPENSES

        const refreshButton =
            document.getElementById("refreshExpenses");

        if (refreshButton) {

            refreshButton.addEventListener("click", function() {

                loadExpenses();

            });

        }

    } catch (error) {

        console.error("Expense initialization error:", error);

        showExpenseMessage(
            "Unable to initialize expenses page: " + error.message,
            "error"
        );

    }

}


// ======================================
// 15. RUN EXPENSE INITIALIZATION
// ======================================

initializeExpensesPage();


// ======================================
// 14. REPORTS & ANALYTICS
// ======================================

let reportSummary = {};
let categoryReports = [];
let monthlyReports = [];
let cropReports = [];
let farmReports = [];
let reportCrops = [];


// ======================================
// 1. REPORT API HELPER
// ======================================

async function reportAPI(url) {

    const { response, result } = await apiRequest(url);

    if (!response.ok || !result.success) {

        throw new Error(
            result.message || "Unable to load report."
        );

    }

    return result;

}


// ======================================
// 2. SAFE HTML
// ======================================

function escapeReportHTML(value) {

    return String(value ?? "").replace(/[&<>"']/g, function(char) {

        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        };

        return entities[char];

    });

}


// ======================================
// 3. CURRENCY FORMAT
// ======================================

function formatReportMoney(amount) {

    return "৳" + Number(amount || 0).toLocaleString(
        "en-BD",
        {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }
    );

}


// ======================================
// 4. REPORT MESSAGE
// ======================================

function showReportMessage(message, color = "red") {

    const messageBox =
        document.getElementById("reportMessage");

    if (!messageBox) return;

    messageBox.textContent = message;
    messageBox.style.color = color;

}


// ======================================
// 5. LOAD REPORT DATA
// ======================================

async function loadReportData(startDate = "", endDate = "") {

    if (!document.getElementById("reportTotalExpenses")) {
        return;
    }

    // Add date parameters only when both dates are provided.
    const query = startDate && endDate
        ? `?start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`
        : "";

    showReportMessage("Loading reports...", "blue");

    try {

        const [
            summaryResult,
            categoryResult,
            monthlyResult,
            cropResult,
            farmResult,
            cropsResult
        ] = await Promise.all([

            reportAPI("/api/reports/summary" + query),

            reportAPI("/api/reports/category" + query),

            reportAPI("/api/reports/monthly" + query),

            reportAPI("/api/reports/crop" + query),

            reportAPI("/api/reports/farm" + query),

            // Crop list is not an expense report, so it does not need date filtering.
            reportAPI("/api/crops")

        ]);

        reportSummary = summaryResult.summary || {};

        categoryReports = categoryResult.categories || [];

        monthlyReports = monthlyResult.monthly || [];

        cropReports = cropResult.crops || [];

        farmReports = farmResult.farms || [];

        reportCrops = cropsResult.crops || [];


        // DISPLAY ALL REPORTS

        displayReportSummary();

        displayCategoryReport();

        displayMonthlyReport();

        displayCropReport();

        displayFarmReport();

        showReportMessage(
            "Reports loaded successfully!",
            "green"
        );

        return true;

    } catch (error) {

        console.error("Report loading error:", error);

        showReportMessage(
            error.message || "Unable to load reports."
        );

        const containers = [
            "categoryExpenseChart",
            "categoryExpenseTable",
            "monthlyExpenseChart",
            "cropExpenseReport",
            "farmExpenseReport"
        ];

        containers.forEach(id => {

            const element = document.getElementById(id);

            if (element) {
                element.innerHTML =
                    '<p class="report-empty-message">Unable to load data.</p>';
            }

        });

        return false;

    }

}


// ======================================
// 6. DISPLAY SUMMARY CARDS
// ======================================

function displayReportSummary() {

    const totalExpenses =
        document.getElementById("reportTotalExpenses");

    const expenseCount =
        document.getElementById("reportExpenseCount");

    const cropCount =
        document.getElementById("reportCropCount");

    const farmCount =
        document.getElementById("reportFarmCount");


    if (totalExpenses) {

        totalExpenses.textContent =
            formatReportMoney(reportSummary.total_expenses);

    }

    if (expenseCount) {

        expenseCount.textContent =
            Number(reportSummary.expense_count || 0);

    }

    if (cropCount) {

        cropCount.textContent =
            reportCrops.length;

    }

    if (farmCount) {

        farmCount.textContent =
            Number(reportSummary.total_farms || 0);

    }

}


// ======================================
// 7. CATEGORY-WISE EXPENSE TABLE
// ======================================

function displayCategoryReport() {

    const container =
        document.getElementById("categoryExpenseTable");

    if (!container) return;

    if (categoryReports.length === 0) {

        container.innerHTML = `
            <p class="report-empty-message">
                No category expense records found.
            </p>
        `;

        return;

    }

    let html = `
        <table class="report-data-table">

            <thead>
                <tr>
                    <th>Expense Category</th>
                    <th>Total Amount</th>
                    <th>Records</th>
                </tr>
            </thead>

            <tbody>
    `;

    categoryReports.forEach(item => {

        html += `
            <tr>

                <td>
                    ${escapeReportHTML(item.expense_type)}
                </td>

                <td>
                    ${formatReportMoney(item.total_amount)}
                </td>

                <td>
                    ${Number(item.expense_count || 0)}
                </td>

            </tr>
        `;

    });

    html += `
            </tbody>
        </table>
    `;

    container.innerHTML = html;

}


// ======================================
// 8. CATEGORY-WISE EXPENSE CHART
// ======================================

function displayCategoryChart() {

    const container =
        document.getElementById("categoryExpenseChart");

    if (!container) return;

    if (categoryReports.length === 0) {

        container.innerHTML = `
            <p class="report-empty-message">
                No category data available for chart.
            </p>
        `;

        return;

    }

    const maxAmount = Math.max(
        ...categoryReports.map(item =>
            Number(item.total_amount || 0)
        ),
        1
    );

    let html = `
        <div class="report-bar-chart">
    `;

    categoryReports.forEach(item => {

        const amount = Number(item.total_amount || 0);

        const percentage =
            (amount / maxAmount) * 100;

        html += `
            <div class="report-bar-item">

                <div class="report-bar-info">

                    <span>
                        ${escapeReportHTML(item.expense_type)}
                    </span>

                    <strong>
                        ${formatReportMoney(amount)}
                    </strong>

                </div>

                <div class="report-bar-track">

                    <div
                        class="report-bar-fill"
                        style="width: ${percentage.toFixed(2)}%"
                    ></div>

                </div>

            </div>
        `;

    });

    html += `
        </div>
    `;

    container.innerHTML = html;

}


// ======================================
// 9. MONTHLY EXPENSE CHART
// ======================================

function displayMonthlyReport() {

    const container =
        document.getElementById("monthlyExpenseChart");

    if (!container) return;

    if (monthlyReports.length === 0) {

        container.innerHTML = `
            <p class="report-empty-message">
                No monthly expense data available.
            </p>
        `;

        return;

    }

    const maxAmount = Math.max(
        ...monthlyReports.map(item =>
            Number(item.total_amount || 0)
        ),
        1
    );

    let html = `
        <div class="monthly-report-chart">
    `;

    monthlyReports.forEach(item => {

        const amount = Number(item.total_amount || 0);

        const percentage =
            (amount / maxAmount) * 100;

        const monthLabel = escapeReportHTML(item.month);

        html += `
            <div class="monthly-report-column">

                <strong class="monthly-report-amount">
                    ${formatReportMoney(amount)}
                </strong>

                <div class="monthly-report-bar-area">

                    <div
                        class="monthly-report-bar"
                        style="height: ${percentage.toFixed(2)}%"
                        title="${formatReportMoney(amount)}"
                    ></div>

                </div>

                <span class="monthly-report-label">
                    ${monthLabel}
                </span>

            </div>
        `;

    });

    html += `
        </div>
    `;

    container.innerHTML = html;

}


// ======================================
// 10. CROP-WISE EXPENSE TABLE
// ======================================

function displayCropReport() {

    const container =
        document.getElementById("cropExpenseReport");

    if (!container) return;

    if (cropReports.length === 0) {

        container.innerHTML = `
            <p class="report-empty-message">
                No crop expense records found.
            </p>
        `;

        return;

    }

    let html = `
        <table class="report-data-table">

            <thead>
                <tr>
                    <th>Crop Name</th>
                    <th>Total Expense</th>
                    <th>Records</th>
                </tr>
            </thead>

            <tbody>
    `;

    cropReports.forEach(item => {

        html += `
            <tr>

                <td>
                    ${escapeReportHTML(item.crop_name)}
                </td>

                <td>
                    ${formatReportMoney(item.total_amount)}
                </td>

                <td>
                    ${Number(item.expense_count || 0)}
                </td>

            </tr>
        `;

    });

    html += `
            </tbody>
        </table>
    `;

    container.innerHTML = html;

}


// ======================================
// 11. FARM-WISE EXPENSE TABLE
// ======================================

function displayFarmReport() {

    const container =
        document.getElementById("farmExpenseReport");

    if (!container) return;

    if (farmReports.length === 0) {

        container.innerHTML = `
            <p class="report-empty-message">
                No farm expense records found.
            </p>
        `;

        return;

    }

    let html = `
        <table class="report-data-table">

            <thead>
                <tr>
                    <th>Farm Name</th>
                    <th>Total Expense</th>
                    <th>Records</th>
                </tr>
            </thead>

            <tbody>
    `;

    farmReports.forEach(item => {

        html += `
            <tr>

                <td>
                    ${escapeReportHTML(item.farm_name)}
                </td>

                <td>
                    ${formatReportMoney(item.total_amount)}
                </td>

                <td>
                    ${Number(item.expense_count || 0)}
                </td>

            </tr>
        `;

    });

    html += `
            </tbody>
        </table>
    `;

    container.innerHTML = html;

}


// ======================================
// 12. REPORT PAGE INITIALIZATION
// ======================================

async function initializeReportsPage() {

    const reportPage =
        document.getElementById("reportTotalExpenses");

    if (!reportPage) return;

    const startDateInput =
        document.getElementById("reportStartDate");

    const endDateInput =
        document.getElementById("reportEndDate");

    const applyFilterButton =
        document.getElementById("applyReportFilter");

    const resetFilterButton =
        document.getElementById("resetReportFilter");

    const filterMessage =
        document.getElementById("reportFilterMessage");


    // APPLY DATE FILTER

    if (applyFilterButton) {

        applyFilterButton.addEventListener("click", async function () {

            const startDate = startDateInput
                ? startDateInput.value
                : "";

            const endDate = endDateInput
                ? endDateInput.value
                : "";

            if (!startDate || !endDate) {

                if (filterMessage) {
                    filterMessage.textContent =
                        "Please select both start date and end date.";
                    filterMessage.style.color = "red";
                }

                return;

            }

            if (startDate > endDate) {

                if (filterMessage) {
                    filterMessage.textContent =
                        "Start date cannot be later than end date.";
                    filterMessage.style.color = "red";
                }

                return;

            }

            if (filterMessage) {
                filterMessage.textContent =
                    "Applying date filter...";
                filterMessage.style.color = "blue";
            }

            const loaded = await loadReportData(startDate, endDate);

            if (filterMessage) {

                if (loaded) {
                    filterMessage.textContent =
                        "Showing reports from " + startDate + " to " + endDate + ".";
                    filterMessage.style.color = "green";
                } else {
                    filterMessage.textContent =
                        "Could not apply the date filter. Please try again.";
                    filterMessage.style.color = "red";
                }

            }

        });

    }


    // RESET DATE FILTER

    if (resetFilterButton) {

        resetFilterButton.addEventListener("click", async function () {

            if (startDateInput) {
                startDateInput.value = "";
            }

            if (endDateInput) {
                endDateInput.value = "";
            }

            if (filterMessage) {
                filterMessage.textContent =
                    "Date filter cleared. Showing all records.";
                filterMessage.style.color = "green";
            }

            await loadReportData();

        });

    }


    // CHECK FARMER SESSION

    try {

        const { response, result } =
            await apiRequest("/api/me");

        if (!response.ok || !result.success) {

            window.location.href =
                "/frontend/login.html";

            return;

        }

        await loadReportData();

    } catch (error) {

        console.error(
            "Reports initialization error:",
            error
        );

        showReportMessage(
            "Unable to initialize reports."
        );

    }

}


// ======================================
// 13. RUN REPORT INITIALIZATION
// ======================================

initializeReportsPage();

// ======================================
// 14. PDF REPORT EXPORT
// ======================================

function exportReportsPDF() {

    const reportContent = document.createElement("div");

    const startDate =
        document.getElementById("reportStartDate")?.value || "";

    const endDate =
        document.getElementById("reportEndDate")?.value || "";

    const dateRange = startDate && endDate
        ? `${startDate} to ${endDate}`
        : "All Records";

    reportContent.innerHTML = `
        <div style="font-family: Arial, sans-serif; padding: 20px; color: #222;">

            <h1 style="text-align: center;">
                Smart Agriculture System
            </h1>

            <h2 style="text-align: center;">
                Expense Reports & Analytics
            </h2>

            <p style="text-align: center;">
                Report Period: ${escapeReportHTML(dateRange)}
            </p>

            <hr>

            <h2>1. Expense Summary</h2>

            <p>
                Total Expenses:
                ${escapeReportHTML(
                    formatReportMoney(reportSummary.total_expenses)
                )}
            </p>

            <p>
                Expense Records:
                ${Number(reportSummary.expense_count || 0)}
            </p>

            <p>
                Total Crops:
                ${reportCrops.length}
            </p>

            <p>
                Total Farms:
                ${Number(reportSummary.total_farms || 0)}
            </p>

            <hr>

            <h2>2. Category-wise Expenses</h2>

            ${document.getElementById("categoryExpenseTable")?.innerHTML || "<p>No data available.</p>"}

            <hr>

            <h2>3. Monthly Expenses</h2>

            ${document.getElementById("monthlyExpenseChart")?.innerHTML || "<p>No data available.</p>"}

            <hr>

            <h2>4. Crop-wise Expenses</h2>

            ${document.getElementById("cropExpenseReport")?.innerHTML || "<p>No data available.</p>"}

            <hr>

            <h2>5. Farm-wise Expenses</h2>

            ${document.getElementById("farmExpenseReport")?.innerHTML || "<p>No data available.</p>"}

            <hr>

            <p style="text-align: center; font-size: 12px;">
                Generated by Smart Agriculture System
            </p>

        </div>
    `;

    const printWindow = window.open("", "_blank");

    if (!printWindow) {

        alert(
            "Please allow pop-ups in your browser to export PDF."
        );

        return;

    }

    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>

            <title>Smart Agriculture Report</title>

            <style>

                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    color: #222;
                }

                h1, h2 {
                    color: #245c3a;
                }

                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }

                th, td {
                    border: 1px solid #ccc;
                    padding: 9px;
                    text-align: left;
                }

                th {
                    background: #e8f2eb;
                }

                .report-bar-chart,
                .monthly-report-chart {
                    margin: 20px 0;
                }

                .report-bar-track {
                    background: #eee;
                    height: 12px;
                }

                .report-bar-fill {
                    background: #398451;
                    height: 12px;
                }

                .monthly-report-bar-area {
                    height: 120px;
                    display: flex;
                    align-items: flex-end;
                }

                .monthly-report-bar {
                    width: 30px;
                    background: #398451;
                }

                @media print {

                    body {
                        margin: 10mm;
                    }

                    table {
                        page-break-inside: avoid;
                    }

                    h2 {
                        page-break-after: avoid;
                    }

                }

            </style>

        </head>

        <body>

            ${reportContent.innerHTML}

        </body>
        </html>
    `);

    printWindow.document.close();

    printWindow.onload = function () {

        printWindow.focus();

        printWindow.print();

    };

}


// ======================================
// 15. INITIALIZE PDF EXPORT BUTTON
// ======================================

const exportPDFButton =
    document.getElementById("exportPDFBtn");

if (exportPDFButton) {

    exportPDFButton.disabled = false;

    exportPDFButton.addEventListener(
        "click",
        exportReportsPDF
    );

}


// HIDE CSV BUTTON (NOT REQUIRED)

const exportCSVButton =
    document.getElementById("exportCSVBtn");

if (exportCSVButton) {

    exportCSVButton.style.display = "none";

}