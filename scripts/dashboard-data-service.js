/**
 * Real-time Data Service for Mission Control Dashboard
 * 
 * This module provides:
 * 1. GitHub API integration for data.json updates
 * 2. Task status synchronization
 * 3. Auto-refresh every 15 minutes
 * 
 * Usage:
 *   node dashboard-data-service.js
 * 
 * Environment variables:
 *   GITHUB_TOKEN - GitHub personal access token
 *   UPDATE_INTERVAL_MS - Update interval (default: 900000 = 15 min)
 */

const fs = require('fs');
const path = require('path');

// Configuration
const REPO = 'chadyi-king/mission-control-dashboard';
const FILE = 'data.json';
const BRANCH = 'main';
const DATA_PATH = path.join(__dirname, '..', 'mission-control-dashboard', 'data.json');

// Load environment
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const UPDATE_INTERVAL = parseInt(process.env.UPDATE_INTERVAL_MS) || 15 * 60 * 1000;

if (!GITHUB_TOKEN) {
    console.error('Error: GITHUB_TOKEN environment variable required');
    process.exit(1);
}

/**
 * Get current file SHA from GitHub
 */
async function getFileSha() {
    const response = await fetch(
        `https://api.github.com/repos/${REPO}/contents/${FILE}?ref=${BRANCH}`,
        {
            headers: {
                'Authorization': `token ${GITHUB_TOKEN}`,
                'Accept': 'application/vnd.github.v3+json'
            }
        }
    );
    
    if (!response.ok) {
        throw new Error(`Failed to get SHA: ${response.status}`);
    }
    
    const data = await response.json();
    return data.sha;
}

/**
 * Update data.json on GitHub
 */
async function updateDataJson() {
    try {
        // Read local data
        const content = fs.readFileSync(DATA_PATH, 'utf8');
        const contentBase64 = Buffer.from(content).toString('base64');
        
        // Get current SHA
        const sha = await getFileSha();
        
        // Update file
        const response = await fetch(
            `https://api.github.com/repos/${REPO}/contents/${FILE}`,
            {
                method: 'PUT',
                headers: {
                    'Authorization': `token ${GITHUB_TOKEN}`,
                    'Content-Type': 'application/json',
                    'Accept': 'application/vnd.github.v3+json'
                },
                body: JSON.stringify({
                    message: `Auto-update data.json - ${new Date().toISOString()}`,
                    content: contentBase64,
                    sha: sha,
                    branch: BRANCH
                })
            }
        );
        
        if (response.ok) {
            console.log(`✅ Data updated at ${new Date().toISOString()}`);
            return true;
        } else {
            const error = await response.text();
            console.error(`❌ Update failed: ${error}`);
            return false;
        }
    } catch (error) {
        console.error(`❌ Error: ${error.message}`);
        return false;
    }
}

/**
 * Update local data.json with current stats
 */
function updateLocalData() {
    try {
        const data = JSON.parse(fs.readFileSync(DATA_PATH, 'utf8'));
        
        // Update timestamp
        data.lastUpdated = new Date().toISOString();
        
        // Update stats (these would come from actual tracking in production)
        data.stats = {
            ...data.stats,
            activeAgents: 1,  // CHAD_YI
            timeActive: calculateTimeActive(),
        };
        
        // Write back
        fs.writeFileSync(DATA_PATH, JSON.stringify(data, null, 2));
        console.log('✅ Local data updated');
        
        return true;
    } catch (error) {
        console.error(`❌ Local update failed: ${error.message}`);
        return false;
    }
}

/**
 * Calculate time active (placeholder)
 */
function calculateTimeActive() {
    // In production, this would track actual session time
    return "00:00";
}

/**
 * Main update loop
 */
async function main() {
    console.log('🚀 Dashboard Data Service starting...');
    console.log(`📊 Update interval: ${UPDATE_INTERVAL / 1000 / 60} minutes`);
    
    // Initial update
    await updateLocalData();
    await updateDataJson();
    
    // Schedule updates
    setInterval(async () => {
        console.log('⏰ Scheduled update...');
        await updateLocalData();
        await updateDataJson();
    }, UPDATE_INTERVAL);
}

// Run if called directly
if (require.main === module) {
    main().catch(console.error);
}

module.exports = { updateDataJson, updateLocalData };
