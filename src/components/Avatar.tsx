import { useEffect, useState } from "react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

export default function () {
  const [avatarSrc, setAvatarSrc] = useState("")

  useEffect(() => {
    const seed = "CallmeLins"
    import("@multiavatar/multiavatar").then(({ default: multiavatar }) => {
      const svg = multiavatar(seed)
      setAvatarSrc(`data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`)
    })
  }, [])

  return (
    <Avatar className="h-20 w-20 transition-transform duration-300 hover:rotate-180">
      <AvatarImage src={avatarSrc || "https://github.com/CallmeLins.png"} alt="icon" />
      <AvatarFallback>林</AvatarFallback>
    </Avatar>
  )
}
