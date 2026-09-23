const express = require('express');
const router = express.Router();
const { exec } = require('child_process');
const db = require('../config/database');
const { authenticateToken, isAdmin } = require('../middleware/auth');
const fs = require('fs');
const path = require('path');

// VULNERABLE ENDPOINT 1 - OS Command Injection via System Info
// This endpoint allows checking system information but is vulnerable to command injection
router.get('/system-info', authenticateToken, isAdmin, async (req, res) => {
  try {
    const { command } = req.query;

    if (!command) {
      return res.status(400).json({ error: 'Command parameter required (e.g., uptime, date, hostname)' });
    }

    // VULNERABILITY: Direct execution of user input without sanitization
    // Allows arbitrary command execution through command chaining
    const fullCommand = `${command}`;
    
    console.log('Executing command:', fullCommand);

    exec(fullCommand, (error, stdout, stderr) => {
      if (error) {
        return res.status(500).json({ 
          error: 'Command execution failed', 
          message: error.message,
          stderr: stderr 
        });
      }

      res.json({
        command: command,
        output: stdout,
        stderr: stderr
      });
    });
  } catch (error) {
    console.error('System info error:', error);
    res.status(500).json({ error: 'Failed to get system info' });
  }
});

// VULNERABLE ENDPOINT 2 - OS Command Injection via Log File Export
// This endpoint exports logs but is vulnerable to command injection
router.post('/export-logs', authenticateToken, isAdmin, async (req, res) => {
  try {
    const { filename, format } = req.body;

    if (!filename) {
      return res.status(400).json({ error: 'Filename required' });
    }

    // VULNERABILITY: Filename is used directly in shell command without validation
    // Allows command injection through filename parameter
    const outputPath = `/tmp/${filename}`;
    let command;

    if (format === 'compressed') {
      command = `tar -czf ${outputPath}.tar.gz /var/log/app.log`;
    } else {
      command = `cp /var/log/app.log ${outputPath}`;
    }

    console.log('Executing log export:', command);

    exec(command, (error, stdout, stderr) => {
      if (error) {
        return res.status(500).json({ 
          error: 'Export failed',
          message: error.message,
          stderr: stderr
        });
      }

      res.json({
        message: 'Logs exported successfully',
        path: outputPath,
        output: stdout
      });
    });
  } catch (error) {
    console.error('Export logs error:', error);
    res.status(500).json({ error: 'Failed to export logs' });
  }
});

// VULNERABLE ENDPOINT 3 - OS Command Injection via Backup Service
// This endpoint creates database backups but is vulnerable to command injection
router.post('/backup', authenticateToken, isAdmin, async (req, res) => {
  try {
    const { backupName, email } = req.body;

    if (!backupName) {
      return res.status(400).json({ error: 'Backup name required' });
    }

    // VULNERABILITY: User input used in shell command without proper sanitization
    // The email parameter allows command injection through command substitution
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${backupName}_${timestamp}.sql`;
    
    let command = `mysqldump -h ${process.env.DB_HOST} -u ${process.env.DB_USER} -p${process.env.DB_PASSWORD} ${process.env.DB_NAME} > /tmp/${filename}`;
    
    if (email) {
      // VULNERABILITY: Email address is not validated and allows command injection
      command += ` && echo "Backup completed" | mail -s "Database Backup" ${email}`;
    }

    console.log('Executing backup command:', command);

    exec(command, { timeout: 30000 }, (error, stdout, stderr) => {
      if (error) {
        return res.status(500).json({ 
          error: 'Backup failed',
          message: error.message,
          stderr: stderr
        });
      }

      res.json({
        message: 'Backup completed successfully',
        filename: filename,
        output: stdout,
        stderr: stderr
      });
    });
  } catch (error) {
    console.error('Backup error:', error);
    res.status(500).json({ error: 'Failed to create backup' });
  }
});

module.exports = router;
