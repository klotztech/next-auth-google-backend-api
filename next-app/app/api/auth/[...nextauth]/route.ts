import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";

const handler = NextAuth({
	providers: [
		GoogleProvider({
			clientId: process.env.GOOGLE_CLIENT_ID,
			clientSecret: process.env.GOOGLE_CLIENT_SECRET,
		}),
	],

	callbacks: {
		async jwt({ account, token, user }) {
			console.log("jwt callback:", {
				account,
				token,
				user,
			});

			// Persist the OAuth access_token to the token right after signin
			if (account) {
				const res = await fetch("http://localhost:8000/token", {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({
						id_token: account.id_token,
					}),
				});

				const tokenRes = await res.json();
				console.log({ tokenRes });

				token.backend_access_token = tokenRes.access_token;
			}
			return token;
		},

		async session({ session, token, user }) {
			// console.log("session callback:", { session, token, user });

			// Send properties to the client, like an access_token for backend access.
			session.backendAccessToken = token.backend_access_token;

			return session;
		},
	},
});

export { handler as GET, handler as POST };
