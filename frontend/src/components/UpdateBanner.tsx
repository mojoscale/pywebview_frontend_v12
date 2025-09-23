import { Alert, Button } from "antd";
import { useUpdate } from "../contexts/UpdateContext";

function UpdateBanner() {
  const { updateInfo } = useUpdate();

  if (!updateInfo) return null;

  const handleUpdate = async () => {
    try {
      // Pass the download_url (or url) to the backend
      const result = await (window as any).pywebview.api.run_update(updateInfo.url);
      console.log("Update result:", result);
    } catch (err) {
      console.error("Failed to trigger update:", err);
    }
  };

  return (
    <div style={{ position: "sticky", top: 0, zIndex: 1000 }}>
      <Alert
        message={`🚀 New version ${updateInfo.version} available`}
        description={
          updateInfo.changelog || "Click below to download and install."
        }
        type="info"
        showIcon
        banner
        action={
          <Button type="primary" onClick={handleUpdate}>
            Update Now
          </Button>
        }
      />
    </div>
  );
}

export default UpdateBanner;
