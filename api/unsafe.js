import { COLORS, SIZES } from "../../constants";
import Text from "../LandingPage/Text";
import { dummyCart as CartData } from "../../data";
import { ReactComponent as Delete } from "../../assets/icons/delete.svg";
import { DownloadIcon } from "../../assets/svg/icons";
import { notify } from "../../features";

const scale = SIZES.scale;

const SingleItem = (props) => {
  const downloadAsset = async () => {
    try {
      let url = props.data?.product?.meta?.cover_image;
      const name = props.data?.product?.title;
      if (!url) throw new Error("Invalid image link");
      const resp = await fetch(url);
      const blob = await resp.blob();
      const objectURL = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = objectURL;
      a.style = "display: none";

      if (name && name.length) a.download = `${name}.jpg`;
      document.body.appendChild(a);
      a.click();
    } catch (error) {
      notify("error", error);
    }
  };

  return (
    <div style={styles.itemContainer}>
      <div style={styles.imageContainer}>
        <img
          style={{ width: 50, height: 50 }}
          src={props.data?.product?.meta?.cover_image}
          alt=""
        />
      </div>
      <div style={styles.descriptionContainer}>
        <div
          style={{
            display: "flex",
            fontSize: 16 * scale,
            color: COLORS.gray1,
            marginRight: 153 * scale,
          }}
        >
          <div style={{ marginRight: 59 * scale }}>
            <Text
              value={<strong>Media Type</strong>}
              marginBottom={12 * scale}
            />
            <Text value={<strong>Size</strong>} marginBottom={12 * scale} />
            <Text value={<strong>License type</strong>} />
          </div>
          <div>
            <Text value="Photos" marginBottom={12 * scale} />
            <Text value="12 x 12" marginBottom={12 * scale} />
            <Text value="Royalty free" />
          </div>
        </div>
        <div
          style={{ display: "flex", fontSize: 16 * scale, color: COLORS.gray1 }}
        >
          <div style={{ marginRight: 51 * scale }}>
            <Text
              value={<strong>Unit Price</strong>}
              marginBottom={30 * scale}
            />
            <Text value={<div className="w3-center">{props.data.price}</div>} />
          </div>
          <div style={{ marginRight: 51 * scale }}>
            <Text value={<strong>Download</strong>} marginBottom={30 * scale} />
            <DownloadIcon onClick={downloadAsset} />
          </div>
        </div>
      </div>
    </div>
  );
};

const OrderItems = ({ order }) => {
  return (
    <div style={{ marginTop: 2 * scale }}>
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Text
          value={order?.unique_order_id}
          color={COLORS.gray1}
          weight={700}
          size={20}
          marginBottom={3}
        />
        {/* <Text
          value={order?.created_at?.slice(0, 10)}
          color={COLORS.gray1}
          marginBottom={3}
        /> */}
        <Text
          value={
            <p>
              <b>status</b>: <i>{order?.status}</i>
            </p>
          }
          color={COLORS.gray1}
          marginBottom={3}
        />
        <Text
          value={
            <p>
              <b>total</b>: &#8358;{order?.total_amount}
            </p>
          }
          color={COLORS.gray1}
          marginBottom={3}
        />
        <Delete width={16 * scale} height={18 * scale} />
      </div>

      <div
        style={{
          paddingBottom: 100 * scale,
          borderTop: `0.3px solid ${COLORS.gray1}`,
        }}
      >
        {order.order_items.map((item, index) => (
          <SingleItem key={index} data={item} />
        ))}
      </div>
    </div>
  );
};

export default OrderItems;

const styles = {
  imageContainer: {
    marginTop: 57 * scale,
    padding: 15,
    border: `5px solid #775050`,
    borderRadius: 2,
    height: "max-content",
  },
  itemContainer: {
    display: "flex",
    justifyContent: "space-between",
  },
  descriptionContainer: {
    paddingLeft: 20 * scale,
    paddingRight: 53 * scale,
    paddingTop: 88 * scale,
    paddingBottom: 46 * scale,
    display: "flex",
    justifyContent: "space-between",
  },
};
