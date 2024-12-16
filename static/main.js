// let map, directionsService, directionsRenderer;
let stopMarkers = [];
var lon_lat = "";
let map, pickupMarker, dropoffMarker, directionsService, directionsRenderer;

function initMap() {
  // Initialize map centered at a default location
  const defaultLocation = { lat: 37.7749, lng: -122.4194 }; // San Francisco, CA
  map = new google.maps.Map(document.getElementById("map"), {
    center: defaultLocation,
    zoom: 13,
  });

  // Initialize markers
  pickupMarker = new google.maps.Marker({
    map: map,
    title: "Pickup Location",
    visible: false,
  });

  dropoffMarker = new google.maps.Marker({
    map: map,
    title: "Drop-off Location",
    visible: false,
  });
  autofillCurrentLocation();
  // Initialize directions service and renderer
  directionsService = new google.maps.DirectionsService();
  directionsRenderer = new google.maps.DirectionsRenderer();
  directionsRenderer.setMap(map);

  // Setup Autocomplete for Pickup
  const pickupInput = document.getElementById("pickup");
  const pickupAutocomplete = new google.maps.places.Autocomplete(pickupInput);
  pickupAutocomplete.bindTo("bounds", map);

  pickupAutocomplete.addListener("place_changed", () => {
    const place = pickupAutocomplete.getPlace();
    if (!place.geometry || !place.geometry.location) {
      alert("No details available for input: '" + place.name + "'");
      return;
    }
    const location_lon_lat = place.geometry.location;
    debugger;

    // Log latitude and longitude for pickup
    console.log(
      `Pickup Location: ${location_lon_lat.lat()}, ${location_lon_lat.lng()}`
    );
    lon_lat = `${location_lon_lat.lat()},${location_lon_lat.lng()}`;
    // Set pickup marker
    pickupMarker.setPosition(place.geometry.location);
    pickupMarker.setVisible(true);
    map.panTo(place.geometry.location);
    calculateRoute();
  });

  // Setup Autocomplete for Drop-off
  const dropoffInput = document.getElementById("dropoff");
  const dropoffAutocomplete = new google.maps.places.Autocomplete(dropoffInput);
  dropoffAutocomplete.bindTo("bounds", map);

  dropoffAutocomplete.addListener("place_changed", () => {
    const place = dropoffAutocomplete.getPlace();
    if (!place.geometry || !place.geometry.location) {
      alert("No details available for input: '" + place.name + "'");
      return;
    }
    console.log(place.name);
    // Set drop-off marker
    dropoffMarker.setPosition(place.geometry.location);
    dropoffMarker.setVisible(true);
    map.panTo(place.geometry.location);
    calculateRoute();
  });
  // Call monitorInputChanges in initMap
}
document.addEventListener("click", function (event) {
  // Check if the clicked element is not an input
  if (!event.target.closest("input")) {
    monitorInputChanges();
  }
});
function monitorInputChanges() {
  // debugger;
  const pickupInput = document.getElementById("pickup");
  const dropoffInput = document.getElementById("dropoff");

  if (!pickupInput.value.trim()) {
    document.getElementById("rideEstimates").style.display = "none";
    pickupMarker.setVisible(false); // Hide the pickup marker if input is cleared
    document.getElementById("ride-types").classList.add("hidden");
  }

  if (!dropoffInput.value.trim()) {
    document.getElementById("rideEstimates").style.display = "none";
    dropoffMarker.setVisible(false); // Hide the dropoff marker if input is cleared
  }
}

function autofillCurrentLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const currentLocation = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        };

        // Update the pickup marker position
        pickupMarker.setPosition(currentLocation);
        pickupMarker.setVisible(true);

        // Pan map to the current location
        map.panTo(currentLocation);

        // Autofill the pickup input with a formatted address
        const geocoder = new google.maps.Geocoder();
        geocoder.geocode({ location: currentLocation }, (results, status) => {
          if (status === "OK" && results[0]) {
            document.getElementById("pickup").value =
              results[0].formatted_address;
          } else {
            console.error("Geocoder failed due to: " + status);
          }
        });
      },
      (error) => {
        alert("Unable to fetch current location: " + error.message);
      }
    );
  } else {
    alert("Geolocation is not supported by this browser.");
  }
}

// Function to calculate and display route
// function calculateRoute() {
//   if (!pickupMarker.getPosition() || !dropoffMarker.getPosition()) return;

//   const request = {
//     origin: pickupMarker.getPosition(),
//     destination: dropoffMarker.getPosition(),
//     travelMode: google.maps.TravelMode.DRIVING,
//   };

//   directionsService.route(request, (result, status) => {
//     if (status === google.maps.DirectionsStatus.OK) {
//       directionsRenderer.setDirections(result);

//       // Extract ETA and Distance
//       const route = result.routes[0].legs[0]; // First leg of the route
//       const eta = route.duration.text; // Example: "15 mins"
//       const distance = route.distance.text; // Example: "5.4 miles"

//       // Update ETA and Distance in the UI
//       document.getElementById("estimatedTime").textContent = eta;
//       document.getElementById("estimatedDistance").textContent = distance;
//     } else {
//       alert("Could not display directions: " + status);
//     }
//   });
// }

function calculateRoute() {
  if (!pickupMarker.getPosition() || !dropoffMarker.getPosition()) return;

  const waypoints = stopMarkers.map((marker) => ({
    location: marker.getPosition(),
    stopover: true,
  }));

  const request = {
    origin: pickupMarker.getPosition(),
    destination: dropoffMarker.getPosition(),
    waypoints: waypoints,
    travelMode: google.maps.TravelMode.DRIVING,
  };

  directionsService.route(request, (result, status) => {
    if (status === google.maps.DirectionsStatus.OK) {
      directionsRenderer.setDirections(result);

      // Extract ETA and Distance
      const route = result.routes[0].legs;
      const totalDuration = route.reduce(
        (sum, leg) => sum + leg.duration.value,
        0
      ); // Duration in seconds
      const totalDistance = route.reduce(
        (sum, leg) => sum + leg.distance.value,
        0
      ); // Distance in meters

      // Update UI
      const totalMinutes = Math.ceil(totalDuration / 60);
      let displayTime;

      if (totalMinutes > 60) {
        const hours = Math.floor(totalMinutes / 60);
        const minutes = totalMinutes % 60;
        displayTime = `${hours} hr${hours > 1 ? "s" : ""} ${minutes} min${
          minutes > 1 ? "s" : ""
        }`;
      } else {
        displayTime = `${totalMinutes} min${totalMinutes > 1 ? "s" : ""}`;
      }

      document.getElementById("estimatedTime").textContent = displayTime;
      document.getElementById("estimatedDistance").textContent =
        (totalDistance / 1609.34).toFixed(2) + " miles";
      document.getElementById("rideEstimates").style.display = "block";
      GetPrice();
    } else {
      alert("Could not display directions: " + status);
    }
  });
}
// Initialize map on page load
window.onload = initMap;

// Update the updateEstimates function to only update ETA and distance
function updateEstimates() {
  const pickup = document.getElementById("pickup").value;
  const dropoff = document.getElementById("dropoff").value;

  if (pickup && dropoff) {
    document.getElementById("rideEstimates").classList.remove("hidden");

    directionsService.route(
      {
        origin: pickup,
        destination: dropoff,
        travelMode: google.maps.TravelMode.DRIVING,
        waypoints: Array.from(document.querySelectorAll("#stopPoints input"))
          .map((input) => ({
            location: input.value,
            stopover: true,
          }))
          .filter((point) => point.location),
      },
      (response, status) => {
        if (status === "OK") {
          directionsRenderer.setDirections(response);
          const route = response.routes[0];
          let totalDistance = 0;
          let totalDuration = 0;

          route.legs.forEach((leg) => {
            totalDistance += leg.distance.value;
            totalDuration += leg.duration.value;
          });

          const miles = (totalDistance / 1609.34).toFixed(1);
          const minutes = Math.round(totalDuration / 60);

          // Update only ETA and distance
          document.getElementById(
            "estimatedTime"
          ).textContent = `${minutes} mins`;
          document.getElementById(
            "estimatedDistance"
          ).textContent = `${miles} miles`;

          updatePrices(miles);

          const bounds = new google.maps.LatLngBounds();
          route.legs.forEach((leg) => {
            bounds.extend(leg.start_location);
            bounds.extend(leg.end_location);
          });
          map.fitBounds(bounds);
        }
      }
    );
  }
}

// Update calculateAndDisplayRoute similarly
function calculateAndDisplayRoute() {
  // document.getElementById("rideClass").style.display = "none";
  if (!directionsService || !directionsRenderer) {
    console.error("Directions services not initialized");
    return;
  }

  const pickup = document.getElementById("pickup");
  const dropoff = document.getElementById("dropoff");

  if (!pickup || !dropoff || !pickup.value || !dropoff.value) {
    alert("Please enter both pickup and drop-off locations");
    return;
  }

  const loadingBar = document.getElementById("loadingBar");
  if (loadingBar) {
    loadingBar.classList.remove("hidden");
  }

  try {
    const waypoints = Array.from(document.querySelectorAll("#stopPoints input"))
      .map((input) => ({
        location: input.value,
        stopover: true,
      }))
      .filter((point) => point.location);

    const request = {
      origin: pickup.value,
      destination: dropoff.value,
      waypoints: waypoints,
      travelMode: google.maps.TravelMode.DRIVING,
    };

    directionsService.route(request, (response, status) => {
      if (status === "OK" && response) {
        directionsRenderer.setDirections(response);

        const route = response.routes[0];
        let totalDistance = 0;
        let totalDuration = 0;

        route.legs.forEach((leg) => {
          if (leg.distance && leg.duration) {
            totalDistance += leg.distance.value;
            totalDuration += leg.duration.value;
          }
        });

        const miles = (totalDistance / 1609.34).toFixed(1);
        const minutes = Math.round(totalDuration / 60);

        // Update only ETA and distance
        document.getElementById(
          "estimatedTime"
        ).textContent = `${minutes} mins`;
        document.getElementById(
          "estimatedDistance"
        ).textContent = `${miles} miles`;
        debugger;
        document.getElementById("rideEstimates").classList.remove("hidden");
        showDriverInfo();

        // Show driver info after a delay
        setTimeout(() => {
          showDriverInfo();
        }, 1000);
      } else {
        if (loadingBar) {
          loadingBar.classList.add("hidden");
        }
        console.error("Directions request failed:", status);
        alert(
          "Could not calculate directions. Please check your locations and try again."
        );
      }
    });
  } catch (error) {
    console.error("Error in calculateAndDisplayRoute:", error);
    if (loadingBar) {
      loadingBar.classList.add("hidden");
    }
    alert("An error occurred while calculating the route. Please try again.");
  }
}

function showDriverInfo() {
  const loadingBar = document.getElementById("loadingBar");
  const driverInfo = document.getElementById("driverInfo");

  // Show loading bar first
  if (loadingBar) {
    loadingBar.classList.remove("hidden");
  }

  // After 2 seconds, hide loading bar and show driver info
  setTimeout(() => {
    if (loadingBar) {
      loadingBar.classList.add("hidden");
    }
    if (driverInfo) {
      driverInfo.classList.remove("hidden");
      // Add animation class
      driverInfo.classList.add("show");
    }
  }, 2000);
}

function updatePrices(miles) {
  const baseRates = {
    economy: 2.5,
    xl: 3.5,
    premium: 4.5,
  };

  document.querySelectorAll(".ride-option").forEach((option) => {
    const type = option.querySelector("h3").textContent.toLowerCase();
    const baseRate = baseRates[type];
    const estimatedPrice = Math.round(baseRate * miles);
    const priceRange = `$${estimatedPrice}-${estimatedPrice + 5}`;
    option.querySelector(".font-bold:last-child").textContent = priceRange;
  });
}

function FillPrices(data) {
  // Select and update the UberX price
  data.forEach((item) => {
    debugger;
    const cabType = item.cab_type;

    // Loop through all labels to find the matching cab type
    const labels = document.querySelectorAll(".grid-cols-2 label");
    labels.forEach((label) => {
      const parentDiv = label.parentElement;

      if (label.textContent.trim() === "Uber" && cabType === "Uber") {
        // Update Uber prices
        if (item.Share && parentDiv.querySelector(".Share")) {
          parentDiv.querySelector(
            ".Share"
          ).textContent = `$${item.Share.toFixed(2)}`;
        }
        if (item.UberX && parentDiv.querySelector(".UberX")) {
          parentDiv.querySelector(
            ".UberX"
          ).textContent = `$${item.UberX.toFixed(2)}`;
        }
        if (item.UberXL && parentDiv.querySelector(".UberXL")) {
          parentDiv.querySelector(
            ".UberXL"
          ).textContent = `$${item.UberXL.toFixed(2)}`;
        }
        if (item.BlackSUV && parentDiv.querySelector(".BlackSUV")) {
          parentDiv.querySelector(
            ".BlackSUV"
          ).textContent = `$${item.BlackSUV.toFixed(2)}`;
        }
      } else if (label.textContent.trim() === "Lyft" && cabType === "Lyft") {
        // Update Lyft prices
        if (item.Share && parentDiv.querySelector(".Share")) {
          parentDiv.querySelector(
            ".Share"
          ).textContent = `$${item.Share.toFixed(2)}`;
        }
        if (item.Lyft && parentDiv.querySelector(".Lyft")) {
          parentDiv.querySelector(".Lyft").textContent = `$${item.Lyft.toFixed(
            2
          )}`;
        }
        if (item.LyftXL && parentDiv.querySelector(".LyftXL")) {
          parentDiv.querySelector(
            ".LyftXL"
          ).textContent = `$${item.LyftXL.toFixed(2)}`;
        }
        if (item.BlackSUV && parentDiv.querySelector(".BlackSUV")) {
          parentDiv.querySelector(
            ".BlackSUV"
          ).textContent = `$${item.BlackSUV.toFixed(2)}`;
        }
      }
    });
  });
}
function addStopPoint() {
  const stopPoints = document.getElementById("stopPoints");
  const stopDiv = document.createElement("div");
  stopDiv.className = "location-input-wrapper stop-point";

  const icon = document.createElement("i");
  icon.className = "fas fa-circle location-icon text-purple-600";

  const input = document.createElement("input");
  input.type = "text";
  input.placeholder = "Add stop";
  input.className = "location-input";

  // Initialize Places Autocomplete for the new stop input
  const stopAutocomplete = new google.maps.places.Autocomplete(input);
  stopAutocomplete.bindTo("bounds", map);

  stopAutocomplete.addListener("place_changed", () => {
    const place = stopAutocomplete.getPlace();
    if (!place.geometry) {
      alert("Please select a location from the dropdown.");
      return;
    }
    const stopMarker = new google.maps.Marker({
      position: place.geometry.location,
      map: map,
      title: "Stop Location",
    });
    stopMarkers.push(stopMarker);
    calculateRoute();
  });

  const removeBtn = document.createElement("button");
  removeBtn.innerHTML = '<i class="fas fa-times"></i>';
  removeBtn.className = "remove-stop";
  removeBtn.onclick = () => {
    stopDiv.remove();
    calculateRoute();
  };

  stopDiv.appendChild(icon);
  stopDiv.appendChild(input);
  stopDiv.appendChild(removeBtn);
  stopPoints.appendChild(stopDiv);
}
function addStop() {
  const stopContainer = document.getElementById("stops-container");
  const stopInput = document.createElement("input");
  stopInput.type = "text";
  stopInput.placeholder = "Enter stop location";
  stopContainer.appendChild(stopInput);

  const stopAutocomplete = new google.maps.places.Autocomplete(stopInput);
  stopAutocomplete.bindTo("bounds", map);

  stopAutocomplete.addListener("place_changed", () => {
    const place = stopAutocomplete.getPlace();
    if (!place.geometry || !place.geometry.location) {
      alert("Invalid stop location.");
      return;
    }

    // Create a marker for the stop
    const stopMarker = new google.maps.Marker({
      position: place.geometry.location,
      map: map,
      title: "Stop Location",
    });
    stopMarkers.push(stopMarker);
    calculateRoute();
  });
}

function selectRide(type, event) {
  document.querySelectorAll(".ride-option").forEach((option) => {
    option.classList.remove("active-ride");
  });
  if (event && event.currentTarget) {
    event.currentTarget.classList.add("active-ride");
  }
}

function selectCabType(event) {
  document.querySelectorAll(".cab-type").forEach((option) => {
    option.classList.remove("activa-cab-type");
  });
  if (event && event.currentTarget) {
    event.currentTarget.classList.add("activa-cab-type");
  }
}

// Event Listeners
document.getElementById("addStop").addEventListener("click", addStopPoint);
document
  .getElementById("bookRide")
  .addEventListener("click", calculateAndDisplayRoute);

document.getElementById("themeToggle").addEventListener("click", () => {
  document.body.classList.toggle("dark-mode");
  const icon = document.querySelector("#themeToggle i");
  icon.classList.toggle("fa-moon");
  icon.classList.toggle("fa-sun");

  // Update map styles when theme changes
  if (map) {
    const isDarkMode = document.body.classList.contains("dark-mode");
    const styles = isDarkMode
      ? [
          { elementType: "geometry", stylers: [{ color: "#242f3e" }] },
          {
            elementType: "labels.text.stroke",
            stylers: [{ color: "#242f3e" }],
          },
          {
            elementType: "labels.text.fill",
            stylers: [{ color: "#746855" }],
          },
          {
            featureType: "road",
            elementType: "geometry",
            stylers: [{ color: "#38414e" }],
          },
          {
            featureType: "road",
            elementType: "geometry.stroke",
            stylers: [{ color: "#212a37" }],
          },
          {
            featureType: "water",
            elementType: "geometry",
            stylers: [{ color: "#17263c" }],
          },
        ]
      : [
          {
            elementType: "geometry",
            stylers: [{ color: "#f5f5f5" }],
          },
          {
            elementType: "labels.icon",
            stylers: [{ visibility: "off" }],
          },
          {
            elementType: "labels.text.fill",
            stylers: [{ color: "#616161" }],
          },
          {
            elementType: "labels.text.stroke",
            stylers: [{ color: "#f5f5f5" }],
          },
          {
            featureType: "road",
            elementType: "geometry",
            stylers: [{ color: "#ffffff" }],
          },
          {
            featureType: "water",
            elementType: "geometry",
            stylers: [{ color: "#c9c9c9" }],
          },
        ];

    map.setOptions({ styles: styles });
  }
});

// Handle map resize for mobile devices
function handleResize() {
  if (map && directionsRenderer) {
    google.maps.event.trigger(map, "resize");
    const currentRoute = directionsRenderer.getDirections();
    if (currentRoute) {
      const bounds = new google.maps.LatLngBounds();
      currentRoute.routes[0].legs.forEach((leg) => {
        bounds.extend(leg.start_location);
        bounds.extend(leg.end_location);
      });
      map.fitBounds(bounds);
    }
  }
}

// Add resize event listener
window.addEventListener("resize", handleResize);

// Set default date and time values when page loads
document.addEventListener("DOMContentLoaded", () => {
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  const formattedDate = tomorrow.toISOString().split("T")[0];
  document.getElementById("scheduleDate").value = formattedDate;

  const hours = String(today.getHours()).padStart(2, "0");
  const minutes = String(today.getMinutes()).padStart(2, "0");
  document.getElementById("scheduleTime").value = `${hours}:${minutes}`;
});
// $("#bookRide").on("click", function () {

// });
function GetPrice() {
  // Get the distance from the <strong> tag and strip " miles"
  let estimatedDistanceText = $("#estimatedDistance").text();
  let estimatedDistance = parseFloat(
    estimatedDistanceText.replace(" miles", "")
  );

  // Create the dummy data with the updated distance value
  let requestData = {
    distance: estimatedDistance,
    lon_lat: lon_lat,
  };

  // Make the AJAX call
  $.ajax({
    url: "/predict",
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify(requestData),
    success: function (response) {
      // Display the prediction result
      debugger;
      console.log(response);
      FillPrices(response);

      document.getElementById("ride-types").classList.remove("hidden");
      document
        .getElementById("inner-container")
        .classList.remove("lg:grid-cols-2");
      document
        .getElementById("inner-container")
        .classList.add("lg:grid-cols-3");
    },
    error: function (xhr, status, error) {
      // Handle any errors
      $("#predictionResult").text("Error: " + xhr.responseJSON.error);
    },
  });
}

// Initialize map when the script loads
window.onload = initMap;
