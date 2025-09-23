import UpdateBanner from "./components/UpdateBanner";

function App() {
  return (
    <div>
      <UpdateBanner />   {/* always mounted, only shows when updateInfo is set */}
      {/* your routes/views go here */}

      <h1>This is version 0.0.2</h1>
    </div>
  );
}


export default App;