export default function LoadingButton({
  loading = false,
  children,
  className = "",
  style,
  disabled,
  loaderVariant = "light",
  type = "button",
  ...props
}) {
  const loaderClass =
    loaderVariant === "dark" ? "button-loader button-loader--dark" : "button-loader";

  return (
    <button
      type={type}
      className={[className, loading ? "btn-loading" : ""].filter(Boolean).join(" ")}
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        ...style,
      }}
      disabled={loading || disabled}
      {...props}
    >
      {loading ? <span className={loaderClass} aria-hidden="true" /> : children}
    </button>
  );
}
