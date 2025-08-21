# 🚀 Mail Merge Kit - Startup Guide

## 🎯 What You Have Now

✅ **Frontend**: React app with template creation and mail merge
✅ **Backend**: Flask API server that processes templates and emails
✅ **Integration**: Frontend and backend are now connected!

## 🚀 How to Run Everything

### **Step 1: Start the Backend (Python API)**

1. **Open a new terminal/command prompt**
2. **Navigate to the Backend folder:**
   ```bash
   cd Backend
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Flask server:**
   ```bash
   python start_server.py
   ```

5. **You should see:**
   ```
   🚀 Starting Mail Merge Kit API Server...
   📍 Server will run on: http://localhost:5000
   🔗 API endpoints available at: http://localhost:5000/api/
   ```

### **Step 2: Start the Frontend (React App)**

1. **Open another terminal/command prompt**
2. **Navigate to the frontend folder:**
   ```bash
   cd frontend
   ```

3. **Start the React development server:**
   ```bash
   npm start
   ```

4. **Your browser should open to:** `http://localhost:3000` (or 3001)

## 🔗 How They Work Together

- **Frontend** (port 3000/3001) ↔ **Backend** (port 5000)
- **Templates** are saved to the backend and loaded from there
- **CSV processing** happens on the backend
- **Email previews** are generated server-side
- **Real email sending** is handled by the backend

## 🧪 Test the Full System

1. **Create a template** on the frontend
2. **Upload a CSV file** with contacts
3. **Select your template** and see the preview
4. **Everything is now connected!** 🎉

## 📧 Optional: Enable Real Email Sending

To send actual emails, create a `.env` file in the Backend folder:

```env
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_SSL=false
EMAIL_USE_STARTTLS=true
```

**Note:** For Gmail, use an App Password, not your regular password.

## 🚨 Troubleshooting

### **Backend won't start?**
- Check if port 5000 is free
- Make sure you're in the Backend folder
- Install requirements: `pip install -r requirements.txt`

### **Frontend can't connect to backend?**
- Make sure backend is running on port 5000
- Check browser console for errors
- Verify both servers are running

### **Port conflicts?**
- Backend: Change port in `start_server.py`
- Frontend: Change port in `package.json` scripts

## 🎉 You're All Set!

Now you have a **fully functional mail merge system**:
- ✨ Beautiful React frontend
- 🔧 Powerful Python backend
- 📧 Real email processing
- 🔗 Seamless integration

**Happy Email Marketing! 🚀**
