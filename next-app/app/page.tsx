"use client";

import { Session } from "next-auth";
import { useSession, signIn, signOut } from "next-auth/react";
import { useCallback, useState } from "react";

export default function Home() {
	const { status, data } = useSession();

	return (
		<main className="flex min-h-screen flex-col items-center justify-between p-24">
			{status === "authenticated" ? (
				<LoggedIn session={data} />
			) : (
				<Login />
			)}
		</main>
	);
}

function Login() {
	return (
		<button
			className="bg-black text-white py-1 px-3"
			onClick={() => signIn()}
		>
			Sign In
		</button>
	);
}

function LoggedIn({ session }: { session: Session }) {
	const { backendAccessToken } = session;
	const [me, setMe] = useState<any>(null);

	const callApi = useCallback(async () => {
		const res = await fetch("http://localhost:8000/me", {
			mode: "cors",
			headers: { Authorization: `Bearer ${backendAccessToken}` },
		});
		const data = await res.json();
		setMe(data);
	}, [backendAccessToken]);

	return (
		<div className="flex flex-col gap-2 items-center">
			Signed in as: {session.user?.email}
			<pre className="whitespace-pre-wrap break-all">
				{JSON.stringify(session, null, 2)}
			</pre>
			<button className="bg-black text-white py-1 px-3" onClick={callApi}>
				Call Backend API
			</button>
			<pre className="whitespace-pre-wrap break-all">
				{JSON.stringify(me, null, 2)}
			</pre>
			<button
				className="bg-black text-white py-1 px-3"
				onClick={() => signOut()}
			>
				Sign Out
			</button>
		</div>
	);
}
