// Testing to see if the endpoint is connectable
// Try this
/*
AKIAQHQ6PGM62T2FFPGU
c7njNpv1oT3rhBhUHue2e2d+oIFnw7QDgCmTtPCG
ap-southeast-2
*/


async function validateAwsCredentials(accessKeyId, secretAccessKey, sessionToken = null) {
    const region = "us-east-1";
    const service = "sts";
    const host = "sts.amazonaws.com";
    const endpoint = `https://${host}/`;

    const body = "Action=GetCallerIdentity&Version=2011-06-15";

    const now = new Date();

    const amzDate = now
        .toISOString()
        .replace(/[:-]|\.\d{3}/g, "");

    const dateStamp = amzDate.substring(0, 8);

    // ---------------------------------------------------------
    // Helpers
    // ---------------------------------------------------------

    const encoder = new TextEncoder();

    async function sha256(data) {
        const hash = await crypto.subtle.digest(
            "SHA-256",
            encoder.encode(data)
        );

        return [...new Uint8Array(hash)]
            .map(b => b.toString(16).padStart(2, "0"))
            .join("");
    }

    async function hmac(key, data) {
        const cryptoKey = await crypto.subtle.importKey(
            "raw",
            typeof key === "string"
                ? encoder.encode(key)
                : key,
            {
                name: "HMAC",
                hash: "SHA-256"
            },
            false,
            ["sign"]
        );

        return new Uint8Array(
            await crypto.subtle.sign(
                "HMAC",
                cryptoKey,
                encoder.encode(data)
            )
        );
    }

    // ---------------------------------------------------------
    // Create canonical request
    // ---------------------------------------------------------

    const payloadHash = await sha256(body);

    let canonicalHeaders =
        `content-type:application/x-www-form-urlencoded; charset=utf-8\n` +
        `host:${host}\n` +
        `x-amz-date:${amzDate}\n`;

    let signedHeaders =
        "content-type;host;x-amz-date";

    if (sessionToken) {
        canonicalHeaders +=
            `x-amz-security-token:${sessionToken}\n`;

        signedHeaders +=
            ";x-amz-security-token";
    }

    const canonicalRequest = [
        "POST",
        "/",
        "",
        canonicalHeaders,
        signedHeaders,
        payloadHash
    ].join("\n");

    // ---------------------------------------------------------
    // Create string to sign
    // ---------------------------------------------------------

    const algorithm = "AWS4-HMAC-SHA256";

    const credentialScope =
        `${dateStamp}/${region}/${service}/aws4_request`;

    const canonicalRequestHash =
        await sha256(canonicalRequest);

    const stringToSign = [
        algorithm,
        amzDate,
        credentialScope,
        canonicalRequestHash
    ].join("\n");

    // ---------------------------------------------------------
    // Calculate signing key
    // ---------------------------------------------------------

    const kDate = await hmac(
        `AWS4${secretAccessKey}`,
        dateStamp
    );

    const kRegion = await hmac(
        kDate,
        region
    );

    const kService = await hmac(
        kRegion,
        service
    );

    const kSigning = await hmac(
        kService,
        "aws4_request"
    );

    const signatureBytes = await hmac(
        kSigning,
        stringToSign
    );

    const signature = [...signatureBytes]
        .map(b => b.toString(16).padStart(2, "0"))
        .join("");

    // ---------------------------------------------------------
    // Authorization header
    // ---------------------------------------------------------

    const authorizationHeader =
        `${algorithm} ` +
        `Credential=${accessKeyId}/${credentialScope}, ` +
        `SignedHeaders=${signedHeaders}, ` +
        `Signature=${signature}`;

    const headers = {
        "Content-Type":
            "application/x-www-form-urlencoded; charset=utf-8",

        "X-Amz-Date": amzDate,

        "Authorization": authorizationHeader
    };

    if (sessionToken) {
        headers["X-Amz-Security-Token"] =
            sessionToken;
    }

    // ---------------------------------------------------------
    // Send request
    // ---------------------------------------------------------

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers,
            body
        });

        const text = await response.text();

        if (!response.ok) {
            return {
                valid: false,
                status: response.status,
                response: text
            };
        }

        // Parse AWS XML response
        const xml = new DOMParser()
            .parseFromString(text, "text/xml");

        const account =
            xml.querySelector("Account")?.textContent;

        const arn =
            xml.querySelector("Arn")?.textContent;

        const userId =
            xml.querySelector("UserId")?.textContent;

        return {
            valid: true,
            account,
            arn,
            userId
        };

    } catch (error) {
        return {
            valid: false,
            error: error.message
        };
    }
}