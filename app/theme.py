def apply_theme(root) -> None:
	try:
		import ttkbootstrap as tb  # type: ignore
		style = tb.Style("flatly")  # alternate: cosmo, flatly, darkly
		style.master = root
	except Exception:
		# Fallback to default theme (do nothing)
		return


