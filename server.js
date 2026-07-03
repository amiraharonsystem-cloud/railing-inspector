const express = require('express');
const exceljs = require('exceljs');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3000;
const FILE_PATH = path.join(__dirname, 'data.xlsx');

app.use(express.json());
app.use(express.static('public')); // מגיש את ממשק המשתמש

app.post('/save', async (req, res) => {
    const { name, email, phone } = req.body;
    const workbook = new exceljs.Workbook();
    let worksheet;

    try {
        if (fs.existsSync(FILE_PATH)) {
            await workbook.xlsx.readFile(FILE_PATH);
            worksheet = workbook.getWorksheet(1);
        } else {
            worksheet = workbook.addWorksheet('Data');
            worksheet.columns = [
                { header: 'שם מלא', key: 'name', width: 20 },
                { header: 'אימייל', key: 'email', width: 25 },
                { header: 'טלפון', key: 'phone', width: 15 },
                { header: 'תאריך יצירה', key: 'date', width: 20 }
            ];
        }

        worksheet.addRow({
            name,
            email,
            phone,
            date: new Date().toLocaleString('he-IL')
        });

        await workbook.xlsx.writeFile(FILE_PATH);
        res.status(200).send({ message: 'הנתונים נשמרו בהצלחה בקובץ!' });
    } catch (error) {
        console.error(error);
        res.status(500).send({ message: 'שגיאה בשמירת הקובץ' });
    }
});

app.listen(PORT, () => {
    console.log(`System running at http://localhost:${PORT}`);
});