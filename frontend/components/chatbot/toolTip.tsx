import { useEffect } from "react";

type Props = {
	text: string;
	showTooltip: boolean;
	setShowTooltip: React.Dispatch<React.SetStateAction<boolean>>;
};
const ToolTip = ({ text, showTooltip, setShowTooltip }: Props) => {
	useEffect(() => {
		const timer = setTimeout(() => {
			setShowTooltip(false);
		}, 5000);

		return () => clearTimeout(timer);
	}, [setShowTooltip]);

	return (
		showTooltip && (
			<div className="fixed bottom-20 right-20 z-40 animate-bounce">
				<div className="bg-black text-white px-3 py-2 rounded-lg text-sm font-medium shadow-lg relative">
					{text}
					<div className="absolute -bottom-1 right-4 w-2 h-2 bg-black rotate-45" />
				</div>
			</div>
		)
	);
};

export default ToolTip;
