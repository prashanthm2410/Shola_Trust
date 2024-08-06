const elephantPrices = {
    'Matriarch': 20000,
    'Tusker': 22000,
    'Baby': 8000,
    'Adolescent': 14000
};

const elephantMaintenanceCostPerDay = 500;
const elephantWorkingDaysPerMonth = 20;
const elephantProfitMargin = 3;

let biomassAmount = 3000;

const biomassRanges = [
    { range: '0-1000', labor: 800, transportation: 200, biomassAmount : 500 },
    { range: '1001-2500', labor: 1500, transportation: 400,biomassAmount : 1750  },
    { range: '2501-5000', labor: 2500, transportation: 700,biomassAmount : 3750  },
    { range: '5001-10000', labor: 4000, transportation: 1200,biomassAmount : 7500  }
];

// const biomassAmount = 3000; 

function updateForm() {
    const selection = document.getElementById('selection').value;
    document.getElementById('elephantForm').style.display = selection === 'elephant' ? 'block' : 'none';
    document.getElementById('biomassForm').style.display = selection === 'biomass' ? 'block' : 'none';

    if (selection === 'biomass') {
        updateBiomassOptions();
    }
}

function updateBiomassOptions() {
    const biomassSelect = document.getElementById('biomassSelect');
    biomassSelect.innerHTML = '';
    biomassRanges.forEach((range, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = `${range.range} kg`;
        biomassSelect.appendChild(option);
    });
}

function calculateRevenue() {
    const selection = document.getElementById('selection').value;
    let resultText = '';

    if (selection === 'elephant') {
        const selectedType = document.getElementById('elephantSelect').value;
        const numberOfElephants = Math.floor(biomassAmount / 200); // Assuming each elephant needs 200 kg of biomass

        const elephantCost = elephantPrices[selectedType];
        const maintenanceCost = elephantMaintenanceCostPerDay * elephantWorkingDaysPerMonth;
        const grossProfitPerElephant = elephantCost * elephantProfitMargin;
        const totalCostForElephants = (elephantCost + maintenanceCost) * numberOfElephants;
        const totalGrossProfit = grossProfitPerElephant * numberOfElephants;
        const netProfit = totalGrossProfit - totalCostForElephants;

        resultText = `Calculation for ${numberOfElephants} elephants:
        Cost per Elephant: ₹${elephantCost.toFixed(2)}
        Monthly Maintenance Cost: ₹${maintenanceCost.toFixed(2)}
        Gross Profit per Elephant: ₹${grossProfitPerElephant.toFixed(2)}
        Total Cost for ${numberOfElephants} Elephants: ₹${totalCostForElephants.toFixed(2)}
        Net Profit for ${numberOfElephants} Elephants: ₹${netProfit.toFixed(2)}`;
    } else if (selection === 'biomass') {
        const biomassCostPrice = parseFloat(document.getElementById('biomassCostPrice').value);
        const biomassSellingPrice = parseFloat(document.getElementById('biomassSellingPrice').value);
        const selectedRangeIndex = parseInt(document.getElementById('biomassSelect').value);

        if (isNaN(biomassCostPrice) || isNaN(biomassSellingPrice)) {
            resultText = "Please enter valid numbers for all fields.";
        } else {
            const selectedRange = biomassRanges[selectedRangeIndex];
            const [minRange, maxRange] = selectedRange.range.split('-').map(Number);

            if (selectedRange.biomassAmount < minRange || selectedRange.biomassAmount > maxRange) {
                resultText = `The entered amount (${selectedRange.biomassAmount} kg) is outside the selected range (${selectedRange.range} kg). Please select the appropriate range.`;
            } else {
                const laborCost = selectedRange.labor;
                const transportationCost = selectedRange.transportation;

                const totalCostPrice = selectedRange.biomassAmount * biomassCostPrice;
                const totalSellingPrice = selectedRange.biomassAmount * biomassSellingPrice;
                const grossProfit = totalSellingPrice - totalCostPrice;
                const totalExpenses = laborCost + transportationCost;
                const netProfit = grossProfit - totalExpenses;
                const areaCleared = selectedRange.biomassAmount / 200;

                resultText = `Calculation for ${selectedRange.biomassAmount} kg of biomass:
                Cost Price: ₹${biomassCostPrice.toFixed(2)} per kg
                Selling Price: ₹${biomassSellingPrice.toFixed(2)} per kg
                Total Cost Price: ₹${totalCostPrice.toFixed(2)}
                Total Selling Price: ₹${totalSellingPrice.toFixed(2)}
                Gross Profit: ₹${grossProfit.toFixed(2)}
                Labor Cost: ₹${laborCost.toFixed(2)}
                Transportation Cost: ₹${transportationCost.toFixed(2)}
                Total Expenses: ₹${totalExpenses.toFixed(2)}
                Net Profit: ₹${netProfit.toFixed(2)}
                Estimated area cleared: ${areaCleared.toFixed(2)} acres`;
            }
        }
    } else {
        resultText = "Please select 'elephant' or 'biomass' option.";
    }

    document.getElementById('result').innerText = resultText;
}
