const FLASK_SUBMIT_URL = 'http://127.0.0.1:8000/participant/submit_result'

export async function POST(request: Request) {
  const headers = new Headers()

  const contentType = request.headers.get('content-type')
  const accept = request.headers.get('accept')
  const cookie = request.headers.get('cookie')

  if (contentType) headers.set('content-type', contentType)
  if (accept) headers.set('accept', accept)
  if (cookie) headers.set('cookie', cookie)

  const response = await fetch(FLASK_SUBMIT_URL, {
    method: 'POST',
    headers,
    body: await request.text(),
    cache: 'no-store',
  })

  const responseHeaders = new Headers()

  const responseContentType = response.headers.get('content-type')
  if (responseContentType) {
    responseHeaders.set('content-type', responseContentType)
  }

  for (const setCookie of response.headers.getSetCookie()) {
    responseHeaders.append('set-cookie', setCookie)
  }

  return new Response(response.body, {
    status: response.status,
    headers: responseHeaders,
  })
}
