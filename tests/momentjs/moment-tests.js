const moment = require('moment');
const fs = require('fs');

// Function to generate unique duration pairs on a logarithmic scale
function generateUniqueLogarithmicDurationPairs(numPairs, maxYears) {
  const pairs = new Map();
  const maxSeconds = maxYears * 365 * 24 * 60 * 60; // Convert years to seconds
  const minLog = Math.log(1); // log(1 second)
  const maxLog = Math.log(maxSeconds); // log(maxSeconds)

  while (pairs.size < numPairs) {
    // Generate a logarithmically spaced value
    const logValue = minLog + (Math.random() * (maxLog - minLog));
    const durationInSeconds = Math.exp(logValue).toFixed(0);

    // Ensure unique durations
    if (!pairs.has(durationInSeconds)) {
      const duration = moment.duration(durationInSeconds, 'seconds');
      const fromNowText = moment().subtract(duration).fromNow();
      pairs.set(durationInSeconds, fromNowText);
    }
  }

  // Convert Map to array and sort by duration
  return Array.from(pairs, ([duration, text]) => ({ duration: parseInt(duration), text }))
    .sort((a, b) => a.duration - b.duration);
}

// Function to convert pairs to CSV
function convertToCSV(pairs) {
  const header = 'Duration,Text\n';
  const rows = pairs.map(pair => `${pair.duration},${pair.text}`).join('\n');
  return header + rows;
}

// Main function to generate CSV file
function generateCSVFile(filename, numPairs, maxYears) {
  const pairs = generateUniqueLogarithmicDurationPairs(numPairs, maxYears);
  const csvContent = convertToCSV(pairs);
  fs.writeFileSync(filename, csvContent, 'utf8');
  console.log(`CSV file '${filename}' generated successfully.`);
}

// Generate CSV file with 10,000 unique pairs ranging from 0 seconds to 100 years
generateCSVFile('durations.csv', 10000, 100);

