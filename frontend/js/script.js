const API_BASE_URL = "";

const form = document.getElementById("prediction-form");
const submitBtn = document.getElementById("submit-btn");
const formError = document.getElementById("form-error");

const cityInput = document.getElementById("city");
const propertyTypeInput = document.getElementById("property_type");
const furnishingInput = document.getElementById("furnishing");
const facingInput = document.getElementById("facing");

const resultEmpty = document.getElementById("result-empty");
const resultLoading = document.getElementById("result-loading");
const resultContent = document.getElementById("result-content");

const priceLakhsEl = document.getElementById("result-price-lakhs");
const priceRupeesEl = document.getElementById("result-price-rupees");
const rangeLowEl = document.getElementById("range-low");
const rangeHighEl = document.getElementById("range-high");

const specCityEl = document.getElementById("spec-city");
const specPropertyTypeEl = document.getElementById("spec-property-type");
const specSqftEl = document.getElementById("spec-sqft");
const specBhkEl = document.getElementById("spec-bhk");
const specFloorsEl = document.getElementById("spec-floors");
const specAgeEl = document.getElementById("spec-age");
const specFurnishingEl = document.getElementById("spec-furnishing");
const specModelEl = document.getElementById("spec-model");

function formatNumber(num) {
  return new Intl.NumberFormat("en-IN").format(num);
}

function showState(state) {
  resultEmpty.hidden = state !== "empty";
  resultLoading.hidden = state !== "loading";
  resultContent.hidden = state !== "content";
}

function showError(message) {
  formError.textContent = message;
  formError.hidden = false;
}

function clearError() {
  formError.hidden = true;
  formError.textContent = "";
}

function populateSelect(selectEl, values) {
  const fragment = document.createDocumentFragment();
  values.forEach((v) => {
    const option = document.createElement("option");
    option.value = v;
    option.textContent = v;
    fragment.appendChild(option);
  });
  selectEl.appendChild(fragment);
}

async function loadMetadata() {
  try {
    const res = await fetch(`${API_BASE_URL}/metadata`);
    if (!res.ok) throw new Error("Failed to fetch metadata");

    const data = await res.json();
    populateSelect(cityInput, data.cities);
    populateSelect(propertyTypeInput, data.property_types);
    populateSelect(furnishingInput, data.furnishing_options);
    populateSelect(facingInput, data.facing_options);
  } catch (err) {
    showError(
      "Could not load city/property option lists. Make sure the backend is running.",
    );
  }
}

async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    const data = await res.json();
    if (!data.model_loaded) {
      showError(
        "Model is still starting up on the server. Try again in a few seconds.",
      );
    }
  } catch (err) {
    showError(
      "Cannot reach the prediction server. Make sure the backend is running on port 8000.",
    );
  }
}

function getFormValues() {
  return {
    city: cityInput.value.trim(),
    property_type: propertyTypeInput.value.trim(),
    facing: facingInput.value.trim(),
    furnishing: furnishingInput.value.trim(),
    lift: document.getElementById("lift").checked ? "Yes" : "No",
    garden: document.getElementById("garden").checked ? "Yes" : "No",
    bedrooms: parseInt(document.getElementById("bedrooms").value, 10),
    bathrooms: parseInt(document.getElementById("bathrooms").value, 10),
    sqft_living: parseFloat(document.getElementById("sqft_living").value),
    sqft_lot: parseFloat(document.getElementById("sqft_lot").value),
    floors: parseInt(document.getElementById("floors").value, 10),
    parking: parseInt(document.getElementById("parking").value, 10),
    nearby_schools: parseInt(
      document.getElementById("nearby_schools").value,
      10,
    ),
    nearby_hospitals: parseInt(
      document.getElementById("nearby_hospitals").value,
      10,
    ),
    balcony: parseInt(document.getElementById("balcony").value, 10),
    age_of_property: parseInt(
      document.getElementById("age_of_property").value,
      10,
    ),
    is_renovated: document.getElementById("is_renovated").checked,
  };
}

function validateFormValues(v) {
  if (!v.city) return "Please enter a city.";
  if (!v.property_type) return "Please enter a property type.";
  if (!v.facing) return "Please enter a facing direction.";
  if (!v.furnishing) return "Please enter a furnishing status.";
  if (!v.sqft_living || v.sqft_living <= 0)
    return "Please enter a valid living area.";
  if (!v.sqft_lot || v.sqft_lot < 0) return "Please enter a valid lot size.";
  if (!v.bedrooms || v.bedrooms <= 0)
    return "Please enter a valid bedroom count.";
  if (!v.bathrooms || v.bathrooms <= 0)
    return "Please enter a valid bathroom count.";
  if (!v.floors || v.floors <= 0) return "Please enter a valid floor count.";
  if (v.parking === null || isNaN(v.parking) || v.parking < 0)
    return "Please enter a valid parking count.";
  if (v.balcony === null || isNaN(v.balcony) || v.balcony < 0)
    return "Please enter a valid balcony count.";
  if (
    v.nearby_schools === null ||
    isNaN(v.nearby_schools) ||
    v.nearby_schools < 0
  )
    return "Please enter a valid nearby schools count.";
  if (
    v.nearby_hospitals === null ||
    isNaN(v.nearby_hospitals) ||
    v.nearby_hospitals < 0
  )
    return "Please enter a valid nearby hospitals count.";
  if (
    v.age_of_property === null ||
    isNaN(v.age_of_property) ||
    v.age_of_property < 0
  )
    return "Please enter a valid property age.";
  if (v.bathrooms > v.bedrooms + 2)
    return "Bathroom count seems unrealistic relative to bedrooms.";
  return null;
}

async function handleSubmit(event) {
  event.preventDefault();
  clearError();

  const values = getFormValues();
  const validationError = validateFormValues(values);
  if (validationError) {
    showError(validationError);
    return;
  }

  submitBtn.disabled = true;
  showState("loading");

  try {
    const res = await fetch(`${API_BASE_URL}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || "Prediction request failed.");
    }

    const data = await res.json();
    renderResult(data, values);
    showState("content");
  } catch (err) {
    showState("empty");
    showError(err.message || "Something went wrong. Please try again.");
  } finally {
    submitBtn.disabled = false;
  }
}

function renderResult(data, inputValues) {
  priceLakhsEl.textContent = data.predicted_price_lakhs.toFixed(2);
  priceRupeesEl.textContent = formatNumber(data.predicted_price_rupees);
  rangeLowEl.textContent = data.confidence_range_lakhs[0].toFixed(2);
  rangeHighEl.textContent = data.confidence_range_lakhs[1].toFixed(2);

  specCityEl.textContent = inputValues.city;
  specPropertyTypeEl.textContent = inputValues.property_type;
  specSqftEl.textContent = `${formatNumber(inputValues.sqft_living)} sq.ft`;
  specBhkEl.textContent = `${inputValues.bedrooms} Bed / ${inputValues.bathrooms} Bath`;
  specFloorsEl.textContent = `${inputValues.floors}`;
  specAgeEl.textContent = `${inputValues.age_of_property} yrs`;
  specFurnishingEl.textContent = inputValues.furnishing;
  specModelEl.textContent = data.model_used;
}

form.addEventListener("submit", handleSubmit);

document.addEventListener("DOMContentLoaded", () => {
  loadMetadata();
  checkHealth();
});
